"""Routing panel for debug toolbar."""

from typing import Dict, Any, Optional

from flaxon.http import Request, Response

from .base import Panel


class RoutingPanel(Panel):
    """Panel displaying route matching information."""
    
    title = "Routing"
    nav_title = "Routes"
    identifier = "routing"
    icon = "🗺️"
    order = 50
    
    has_three_scene = True
    three_scene_class = "RoutingScene"
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        # This would integrate with Flaxon's router
        return {
            "matched_route": None,
            "route_params": {},
            "route_name": None,
            "all_routes": [],
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        # Get route info from app
        app = self._get_app()
        if app and hasattr(app, "router"):
            self._data.update({
                "all_routes": self._get_all_routes(app),
            })
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        matched_route = self._data.get("matched_route", "No route matched")
        route_params = self._data.get("route_params", {})
        route_name = self._data.get("route_name", "unnamed")
        all_routes = self._data.get("all_routes", [])
        
        # Build routes table
        routes_rows = ""
        for route in all_routes[:50]:  # Limit to 50
            routes_rows += f"""
                <div class="route-row">
                    <span class="route-method">{route.get('method', 'GET')}</span>
                    <span class="route-path">{route.get('path', '/')}</span>
                    <span class="route-name">{route.get('name', '-')}</span>
                </div>
            """
        
        return f"""
        <div class="routing-panel">
            <!-- Three.js 3D Visualization -->
            <div class="three-container" id="routing-three-scene">
                <canvas id="routing-canvas"></canvas>
            </div>
            
            <!-- Matched Route -->
            <div class="matched-route">
                <div class="route-summary">
                    <span class="route-label">Matched Route:</span>
                    <span class="route-value">{matched_route}</span>
                </div>
                <div class="route-summary">
                    <span class="route-label">Route Name:</span>
                    <span class="route-value">{route_name}</span>
                </div>
                <div class="route-summary">
                    <span class="route-label">Parameters:</span>
                    <span class="route-value">{route_params if route_params else 'None'}</span>
                </div>
            </div>
            
            <!-- All Routes -->
            <div class="route-list">
                <h4>All Routes ({len(all_routes)})</h4>
                <div class="route-table">
                    <div class="route-header">
                        <span class="route-method">Method</span>
                        <span class="route-path">Path</span>
                        <span class="route-name">Name</span>
                    </div>
                    {routes_rows}
                </div>
            </div>
        </div>
        
        <style>
            .matched-route {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 16px;
            }}
            
            .route-summary {{
                display: flex;
                padding: 4px 0;
                font-size: 13px;
            }}
            
            .route-label {{
                min-width: 120px;
                font-weight: 500;
                color: var(--text-muted, #888);
            }}
            
            .route-value {{
                font-family: monospace;
                color: var(--text, #e0e0e0);
            }}
            
            .route-table {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                overflow: hidden;
                font-size: 13px;
                max-height: 300px;
                overflow-y: auto;
            }}
            
            .route-header, .route-row {{
                display: flex;
                align-items: center;
                padding: 6px 12px;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .route-header {{
                font-weight: 600;
                color: var(--text-muted, #888);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: var(--bg-primary, #1a1a2e);
                position: sticky;
                top: 0;
                z-index: 1;
            }}
            
            .route-method {{ width: 70px; font-weight: 600; font-size: 11px; text-transform: uppercase; }}
            .route-path {{ flex: 1; font-family: monospace; font-size: 12px; }}
            .route-name {{ width: 150px; font-size: 12px; color: var(--text-muted, #888); }}
            
            .route-method.get {{ color: #4CAF50; }}
            .route-method.post {{ color: #FF9800; }}
            .route-method.put {{ color: #2196F3; }}
            .route-method.delete {{ color: #f44336; }}
            .route-method.patch {{ color: #9C27B0; }}
            
            .route-row:hover {{
                background: var(--hover, #2a2a4e);
            }}
            
            #routing-three-scene {{
                height: 250px;
                margin-bottom: 16px;
                border-radius: 8px;
                overflow: hidden;
                background: var(--three-bg, #0d0d1a);
            }}
        </style>
        """
    
    def _get_app(self):
        """Get the Flaxon app instance."""
        # This would be injected by the plugin
        return None
    
    def _get_all_routes(self, app) -> list:
        """Get all registered routes."""
        routes = []
        if hasattr(app, "router") and hasattr(app.router, "_routes"):
            for route in app.router._routes:
                routes.append({
                    "method": route.method,
                    "path": route.path,
                    "name": getattr(route, "name", None),
                })
        return routes