"""Debug toolbar middleware for Flaxon."""

import time
import json
from typing import Callable, Optional, Dict, Any

from flaxon.http import Request, Response


class DebugToolbarMiddleware:
    """ASGI middleware that captures request/response data for the debug toolbar."""
    
    def __init__(self, app: Callable, plugin_instance):
        self.app = app
        self.plugin = plugin_instance
        self.config = plugin_instance.config
    
    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive, self.plugin._app)
        
        if self._should_skip(request):
            await self.app(scope, receive, send)
            return
        
        await self.plugin.process_request(request)
        response_data = []
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_data.append({
                    "type": "start",
                    "status": message.get("status", 200),
                    "headers": dict(message.get("headers", [])),
                })
            elif message["type"] == "http.response.body":
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
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            await self.plugin.process_response(request, None)
            raise
        
        response = self._build_response(response_data)
        await self.plugin.process_response(request, response)
        
        if response and self._is_html_response(response):
            await self._inject_toolbar(response)
    
    def _should_skip(self, request: Request) -> bool:
        path = request.path
        if path.startswith(("/static/", "/assets/", "/css/", "/js/", "/favicon")):
            return True
        if path.startswith("/api/"):
            return True
        if path.startswith("/_debug_toolbar/"):
            return True
        return False
    
    def _is_html_response(self, response: Response) -> bool:
        content_type = response.headers.get("content-type", "")
        return "text/html" in content_type.lower()
    
    def _build_response(self, response_data: list) -> Optional[Response]:
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
        toolbar_html = self._build_toolbar_html()
        
        content = response.content.decode("utf-8", errors="replace")
        insert_pos = content.lower().find("</body>")
        
        if insert_pos != -1:
            modified = content[:insert_pos] + toolbar_html + content[insert_pos:]
            encoded_content = modified.encode("utf-8")
            response.content = encoded_content
            response.headers["content-length"] = str(len(encoded_content))

    def _build_toolbar_html(self) -> str:
        panels = self.plugin.get_enabled_panels()
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
                    <div class="panel-content"></div>
                </div>
            """
        
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
        
        <script>
            (function() {{
                const toolbar = document.getElementById('flaxon-debug-toolbar');
                const header = toolbar.querySelector('.toolbar-header');
                const toggleBtn = toolbar.querySelector('.toolbar-toggle');
                const closeBtn = toolbar.querySelector('.toolbar-close');
                const tabs = toolbar.querySelectorAll('.toolbar-tab');
                const panels = toolbar.querySelectorAll('.toolbar-panel');
                const threeConfig = {json.dumps(self.plugin.get_three_config())};
                
                header.addEventListener('click', function(e) {{
                    if (e.target.closest('.toolbar-controls')) return;
                    toolbar.classList.toggle('collapsed');
                    const icon = toggleBtn.querySelector('.toggle-icon');
                    if (icon) {{
                        icon.textContent = toolbar.classList.contains('collapsed') ? '▲' : '▼';
                    }}
                }});
                
                closeBtn.addEventListener('click', function() {{
                    toolbar.style.display = 'none';
                }});
                
                tabs.forEach(function(tab) {{
                    tab.addEventListener('click', function() {{
                        const panelId = this.dataset.panel;
                        tabs.forEach(t => t.classList.remove('active'));
                        this.classList.add('active');
                        
                        panels.forEach(p => p.classList.remove('active'));
                        const panel = document.getElementById('panel-' + panelId);
                        if (panel) {{
                            panel.classList.add('active');
                            loadPanel(panelId, panel);
                        }}
                    }});
                }});
                
                async function loadPanel(panelId, container) {{
                    container.querySelector('.panel-content').innerHTML = 
                        '<div style="text-align:center;padding:40px;">Loading...</div>';
                    
                    try {{
                        const response = await fetch('/_debug_toolbar/panels/' + panelId);
                        if (response.ok) {{
                            const html = await response.text();
                            container.querySelector('.panel-content').innerHTML = html;
                        }}
                    }} catch (error) {{
                        container.querySelector('.panel-content').innerHTML = 
                            '<div style="text-align:center;padding:40px;color:red;">Error loading panel</div>';
                    }}
                }}
                
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