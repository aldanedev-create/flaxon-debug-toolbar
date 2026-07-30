"""Debug toolbar middleware for Flaxon."""

import time
import json
from typing import Callable, Optional, Dict, Any
from urllib.parse import urlparse

from flaxon.http import Request, Response


class DebugToolbarMiddleware:
    """
    ASGI middleware that captures request/response data for the debug toolbar.
    
    Features:
        - Captures request and response data
        - Measures timing
        - Injects toolbar HTML into responses
        - Handles redirect interception
    """
    
    def __init__(self, app: Callable, plugin_instance):
        """
        Initialize debug toolbar middleware.
        
        Args:
            app: ASGI application
            plugin_instance: DebugToolbarPlugin instance
        """
        self.app = app
        self.plugin = plugin_instance
        self.config = plugin_instance.config
    
    async def __call__(self, scope, receive, send):
        """ASGI callable with debug toolbar handling."""
        
        # Only handle HTTP requests
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        
        # Create request object
        request = Request(scope, receive, self.plugin._app)
        
        # Skip toolbar for static assets and API requests
        if self._should_skip(request):
            await self.app(scope, receive, send)
            return
        
        # Process request
        await self.plugin.process_request(request)
        
        # Store request for later
        start_time = time.time()
        
        # Capture response
        response_data = []
        
        async def send_wrapper(message):
            """Wrap send to capture response data."""
            if message["type"] == "http.response.start":
                # Store status
                response_data.append({
                    "type": "start",
                    "status": message.get("status", 200),
                    "headers": dict(message.get("headers", [])),
                })
            elif message["type"] == "http.response.body":
                # Store body
                response_data.append({
                    "type": "body",
                    "body": message.get("body", b""),
                    "more_body": message.get("more_body", False),
                })
            elif message["type"] == "http.response.push":
                response_data.append({
                    "type": "push",
                    "path": message.get("path", ""),
                    "headers": dict(message.get("headers", [])),
                })
            
            # Pass through
            await send(message)
        
        # Execute app with wrapped send
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Capture error
            await self.plugin.process_response(request, None)
            raise
        
        # Process response
        response = self._build_response(response_data)
        await self.plugin.process_response(request, response)
        
        # Inject toolbar if HTML response
        if response and self._is_html_response(response):
            await self._inject_toolbar(response)
    
    def _should_skip(self, request: Request) -> bool:
        """
        Check if request should skip toolbar.
        
        Args:
            request: Current request
            
        Returns:
            True if should skip
        """
        path = request.path
        
        # Skip static assets
        if path.startswith(("/static/", "/assets/", "/css/", "/js/", "/favicon")):
            return True
        
        # Skip API requests
        if path.startswith("/api/"):
            return True
        
        # Skip toolbar assets
        if path.startswith("/_debug_toolbar/"):
            return True
        
        return False
    
    def _is_html_response(self, response: Response) -> bool:
        """
        Check if response is HTML.
        
        Args:
            response: Response
            
        Returns:
            True if HTML
        """
        content_type = response.headers.get("content-type", "")
        return "text/html" in content_type.lower()
    
    def _build_response(self, response_data: list) -> Optional[Response]:
        """
        Build response from captured data.
        
        Args:
            response_data: Captured response data
            
        Returns:
            Response or None
        """
        if not response_data:
            return None
        
        status = 200
        headers = {}
        body = b""
        
        for item in response_data:
            if item["type"] == "start":
                status = item.get("status", 200)
                headers = item.get("headers", {})
            elif item["type"] == "body":
                body += item.get("body", b"")
        
        return Response(
            content=body,
            status_code=status,
            headers=headers,
        )
    
    async def _inject_toolbar(self, response: Response) -> None:
        """
        Inject toolbar HTML into response.
        
        Args:
            response: Response
        """
        # Build toolbar HTML
        toolbar_html = self._build_toolbar_html()
        
        # Inject before </body>
        content = response.content.decode("utf-8")
        
        # Find </body> tag
        insert_pos = content.lower().find("</body>")
        if insert_pos != -1:
            modified = content[:insert_pos] + toolbar_html + content[insert_pos:]
            response.content = modified.encode("utf-8")
            response.headers["content-length"] = str(len(response.content))
    
    def _build_toolbar_html(self) -> str:
        """
        Build toolbar HTML.
        
        Returns:
            Toolbar HTML
        """
        # Get enabled panels
        panels = self.plugin.get_enabled_panels()
        
        # Build panel tabs
        tabs_html = ""
        content_html = ""
        
        for i, panel in enumerate(panels):
            active = "active" if i == 0 else ""
            tabs_html += f"""
                <button class="toolbar-tab {active}" data-panel="{panel.identifier}">
                    {panel.icon} {panel.nav_title}
                </button>
            """
            
            content_html += f"""
                <div class="toolbar-panel {active}" id="panel-{panel.identifier}">
                    <div class="panel-content">
                        <!-- Panel content will be loaded via JS -->
                    </div>
                </div>
            """
        
        # Build theme class
        theme_class = f"theme-{self.config.theme}"
        three_class = "three-enabled" if self.config.three_enabled else ""
        
        return f"""
        <!-- Flaxon Debug Toolbar -->
        <div id="flaxon-debug-toolbar" class="{theme_class} {three_class}" data-position="{self.config.position}">
            <div class="toolbar-container">
                <div class="toolbar-header">
                    <div class="toolbar-title">
                        <span class="toolbar-logo">🐛</span>
                        <span class="toolbar-name">Flaxon Debug Toolbar</span>
                        <span class="toolbar-version">v{self.plugin.version}</span>
                    </div>
                    <div class="toolbar-controls">
                        <button class="toolbar-toggle" title="Toggle toolbar">
                            <span class="toggle-icon">▼</span>
                        </button>
                        <button class="toolbar-close" title="Close toolbar">✕</button>
                    </div>
                </div>
                
                <div class="toolbar-tabs">
                    {tabs_html}
                </div>
                
                <div class="toolbar-panels">
                    {content_html}
                </div>
            </div>
        </div>
        
        <style>
            /* Inline critical styles */
            #flaxon-debug-toolbar {{
                position: fixed;
                {self.config.position}: 0;
                left: 0;
                right: 0;
                z-index: 99999;
                font-family: system-ui, -apple-system, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                max-height: 80vh;
                overflow: hidden;
                transition: transform 0.3s ease;
                background: {self._get_theme_color('background')};
                color: {self._get_theme_color('text')};
                border-top: 2px solid {self._get_theme_color('border')};
                box-shadow: 0 -4px 20px rgba(0,0,0,0.3);
            }}
            
            #flaxon-debug-toolbar.collapsed {{
                transform: translateY(calc(100% - 40px));
            }}
            
            .toolbar-container {{
                display: flex;
                flex-direction: column;
                height: 100%;
                max-height: 80vh;
            }}
            
            .toolbar-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 8px 16px;
                background: {self._get_theme_color('header')};
                border-bottom: 1px solid {self._get_theme_color('border')};
                cursor: pointer;
                flex-shrink: 0;
            }}
            
            .toolbar-title {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
            }}
            
            .toolbar-logo {{
                font-size: 20px;
            }}
            
            .toolbar-version {{
                font-size: 11px;
                opacity: 0.7;
                font-weight: normal;
            }}
            
            .toolbar-controls {{
                display: flex;
                gap: 8px;
            }}
            
            .toolbar-controls button {{
                background: none;
                border: none;
                color: inherit;
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 14px;
                opacity: 0.7;
                transition: opacity 0.2s;
            }}
            
            .toolbar-controls button:hover {{
                opacity: 1;
                background: {self._get_theme_color('hover')};
            }}
            
            .toolbar-tabs {{
                display: flex;
                overflow-x: auto;
                padding: 4px 8px;
                background: {self._get_theme_color('tabs')};
                border-bottom: 1px solid {self._get_theme_color('border')};
                flex-shrink: 0;
                gap: 2px;
            }}
            
            .toolbar-tab {{
                padding: 6px 12px;
                border: none;
                background: none;
                color: {self._get_theme_color('text_muted')};
                cursor: pointer;
                border-radius: 4px;
                font-size: 13px;
                transition: all 0.2s;
                white-space: nowrap;
            }}
            
            .toolbar-tab:hover {{
                background: {self._get_theme_color('hover')};
                color: {self._get_theme_color('text')};
            }}
            
            .toolbar-tab.active {{
                background: {self._get_theme_color('active')};
                color: {self._get_theme_color('text')};
                font-weight: 500;
            }}
            
            .toolbar-panels {{
                flex: 1;
                overflow: auto;
                padding: 16px;
            }}
            
            .toolbar-panel {{
                display: none;
                height: 100%;
            }}
            
            .toolbar-panel.active {{
                display: block;
            }}
            
            .panel-content {{
                height: 100%;
                overflow: auto;
            }}
            
            /* Three.js container */
            .three-container {{
                width: 100%;
                height: 300px;
                border-radius: 8px;
                overflow: hidden;
                margin-bottom: 16px;
                background: {self._get_theme_color('three_bg')};
            }}
            
            .three-container canvas {{
                width: 100% !important;
                height: 100% !important;
                display: block;
            }}
            
            /* Dark theme specific */
            .theme-dark {{
                --bg: #1a1a2e;
                --text: #e0e0e0;
                --text-muted: #888;
                --border: #2a2a3e;
                --header: #16213e;
                --tabs: #1a1a2e;
                --hover: #2a2a4e;
                --active: #0f3460;
                --three-bg: #0d0d1a;
            }}
            
            /* Light theme specific */
            .theme-light {{
                --bg: #f5f5f5;
                --text: #333;
                --text-muted: #888;
                --border: #ddd;
                --header: #e8e8e8;
                --tabs: #f5f5f5;
                --hover: #e0e0e0;
                --active: #d0d0d0;
                --three-bg: #f0f0f0;
            }}
            
            /* Responsive */
            @media (max-width: 768px) {{
                .toolbar-tabs {{
                    flex-wrap: nowrap;
                    overflow-x: auto;
                }}
                
                .toolbar-tab {{
                    font-size: 12px;
                    padding: 4px 8px;
                }}
            }}
        </style>
        
        <script>
            // Toolbar JavaScript
            (function() {{
                const toolbar = document.getElementById('flaxon-debug-toolbar');
                const header = toolbar.querySelector('.toolbar-header');
                const toggleBtn = toolbar.querySelector('.toolbar-toggle');
                const closeBtn = toolbar.querySelector('.toolbar-close');
                const tabs = toolbar.querySelectorAll('.toolbar-tab');
                const panels = toolbar.querySelectorAll('.toolbar-panel');
                const threeConfig = {json.dumps(self.plugin.get_three_config())};
                
                // Toggle collapse
                header.addEventListener('click', function(e) {{
                    if (e.target.closest('.toolbar-controls')) return;
                    toolbar.classList.toggle('collapsed');
                    const icon = toggleBtn.querySelector('.toggle-icon');
                    if (icon) {{
                        icon.textContent = toolbar.classList.contains('collapsed') ? '▲' : '▼';
                    }}
                }});
                
                // Close toolbar
                closeBtn.addEventListener('click', function() {{
                    toolbar.style.display = 'none';
                }});
                
                // Switch panels
                tabs.forEach(function(tab) {{
                    tab.addEventListener('click', function() {{
                        const panelId = this.dataset.panel;
                        
                        // Update tabs
                        tabs.forEach(t => t.classList.remove('active'));
                        this.classList.add('active');
                        
                        // Update panels
                        panels.forEach(p => p.classList.remove('active'));
                        const panel = document.getElementById('panel-' + panelId);
                        if (panel) {{
                            panel.classList.add('active');
                            // Load panel content
                            loadPanel(panelId, panel);
                        }}
                    }});
                }});
                
                // Load panel content
                async function loadPanel(panelId, container) {{
                    // Show loading
                    container.querySelector('.panel-content').innerHTML = 
                        '<div style="text-align:center;padding:40px;">Loading...</div>';
                    
                    try {{
                        const response = await fetch('/_debug_toolbar/panels/' + panelId);
                        if (response.ok) {{
                            const html = await response.text();
                            container.querySelector('.panel-content').innerHTML = html;
                            
                            // Initialize Three.js if enabled
                            if (threeConfig.enabled && panelId === 'timeline') {{
                                initThreeTimeline();
                            }}
                            if (threeConfig.enabled && panelId === 'sql') {{
                                initThreeSQL();
                            }}
                        }}
                    }} catch (error) {{
                        container.querySelector('.panel-content').innerHTML = 
                            '<div style="text-align:center;padding:40px;color:red;">Error loading panel</div>';
                    }}
                }}
                
                // Initialize Three.js timeline
                function initThreeTimeline() {{
                    // Three.js initialization code
                    // This would be loaded from the static JS file
                }}
                
                // Initialize Three.js SQL visualization
                function initThreeSQL() {{
                    // Three.js initialization code
                }}
                
                // Load initial panel
                const activeTab = document.querySelector('.toolbar-tab.active');
                if (activeTab) {{
                    const panelId = activeTab.dataset.panel;
                    const panel = document.getElementById('panel-' + panelId);
                    if (panel) {{
                        loadPanel(panelId, panel);
                    }}
                }}
            }})();
        </script>
        """
    
    def _get_theme_color(self, key: str) -> str:
        """Get theme color."""
        colors = {
            "dark": {
                "background": "#1a1a2e",
                "text": "#e0e0e0",
                "text_muted": "#888",
                "border": "#2a2a3e",
                "header": "#16213e",
                "tabs": "#1a1a2e",
                "hover": "#2a2a4e",
                "active": "#0f3460",
                "three_bg": "#0d0d1a",
            },
            "light": {
                "background": "#f5f5f5",
                "text": "#333",
                "text_muted": "#888",
                "border": "#ddd",
                "header": "#e8e8e8",
                "tabs": "#f5f5f5",
                "hover": "#e0e0e0",
                "active": "#d0d0d0",
                "three_bg": "#f0f0f0",
            }
        }
        return colors.get(self.config.theme, colors["dark"]).get(key, "#333")