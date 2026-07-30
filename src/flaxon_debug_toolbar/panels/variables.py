"""Variables panel for debug toolbar."""

from typing import Dict, Any

from flaxon.http import Request, Response

from .base import Panel


class VariablesPanel(Panel):
    """Panel displaying request, session, state, and config variables."""
    
    title = "Variables"
    nav_title = "Variables"
    identifier = "variables"
    icon = "📦"
    order = 90
    
    has_three_scene = False
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        return {
            "request_vars": {},
            "session_vars": {},
            "state_vars": {},
            "config_vars": {},
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        # Collect request variables
        request_vars = {
            "method": request.method,
            "path": request.path,
            "url": str(request.url),
            "client_ip": request.client[0] if request.client else None,
            "headers": dict(request.headers),
            "query": dict(request.query_params),
        }
        
        # Collect session variables
        session_vars = {}
        if hasattr(request, "session") and request.session:
            session_vars = dict(request.session)
        
        # Collect state variables
        state_vars = {}
        if hasattr(request, "state"):
            state_vars = self._get_state_vars(request.state)
        
        # Collect config variables
        config_vars = {}
        app = self._get_app()
        if app and hasattr(app, "config"):
            config_vars = dict(app.config) if isinstance(app.config, dict) else {}
        
        self._data = {
            "request_vars": self._sanitize_vars(request_vars),
            "session_vars": self._sanitize_vars(session_vars),
            "state_vars": self._sanitize_vars(state_vars),
            "config_vars": self._sanitize_vars(config_vars),
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        request_vars = self._data.get("request_vars", {})
        session_vars = self._data.get("session_vars", {})
        state_vars = self._data.get("state_vars", {})
        config_vars = self._data.get("config_vars", {})
        
        return f"""
        <div class="variables-panel">
            <div class="variables-grid">
                <!-- Request Variables -->
                <div class="variables-section">
                    <h4>📨 Request Variables</h4>
                    <div class="variables-table">
                        {self._render_vars(request_vars)}
                    </div>
                </div>
                
                <!-- Session Variables -->
                <div class="variables-section">
                    <h4>🔑 Session Variables</h4>
                    <div class="variables-table">
                        {self._render_vars(session_vars)}
                    </div>
                </div>
                
                <!-- State Variables -->
                <div class="variables-section">
                    <h4>📦 State Variables</h4>
                    <div class="variables-table">
                        {self._render_vars(state_vars)}
                    </div>
                </div>
                
                <!-- Config Variables -->
                <div class="variables-section">
                    <h4>⚙️ Config Variables</h4>
                    <div class="variables-table">
                        {self._render_vars(config_vars)}
                    </div>
                </div>
            </div>
        </div>
        
        <style>
            .variables-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }}
            
            @media (max-width: 768px) {{
                .variables-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
            
            .variables-section {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                padding: 12px 16px;
            }}
            
            .variables-section h4 {{
                margin: 0 0 8px 0;
                font-size: 13px;
                text-transform: uppercase;
                color: var(--text-muted, #888);
                letter-spacing: 0.5px;
            }}
            
            .variables-table {{
                font-size: 12px;
                font-family: monospace;
                max-height: 200px;
                overflow-y: auto;
            }}
            
            .var-row {{
                display: flex;
                padding: 3px 0;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .var-key {{
                min-width: 150px;
                font-weight: 500;
                color: var(--text-muted, #888);
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
            
            .var-value {{
                flex: 1;
                word-break: break-all;
                color: var(--text, #e0e0e0);
            }}
            
            .var-value.null {{
                color: var(--text-muted, #888);
                font-style: italic;
            }}
            
            .var-value.string {{
                color: #4CAF50;
            }}
            
            .var-value.number {{
                color: #FF9800;
            }}
            
            .var-value.boolean {{
                color: #2196F3;
            }}
            
            .var-value.array {{
                color: #9C27B0;
            }}
            
            .var-value.object {{
                color: #00BCD4;
            }}
        </style>
        """
    
    def _render_vars(self, vars_dict: Dict[str, Any]) -> str:
        """Render variables as HTML."""
        if not vars_dict:
            return "<div class='empty'>No variables</div>"
        
        rows = []
        for key, value in vars_dict.items():
            value_type = self._get_value_type(value)
            value_str = self._format_value(value)
            rows.append(f"""
                <div class="var-row">
                    <span class="var-key">{key}</span>
                    <span class="var-value {value_type}">{value_str}</span>
                </div>
            """)
        return "".join(rows)
    
    def _get_value_type(self, value: Any) -> str:
        """Get the type of a value."""
        if value is None:
            return "null"
        if isinstance(value, str):
            return "string"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "object"
        return "unknown"
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if value is None:
            return "null"
        if isinstance(value, str):
            if len(value) > 100:
                return value[:100] + "..."
            return value
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, list):
            if len(value) > 5:
                return f"[{len(value)} items]"
            return str(value)
        if isinstance(value, dict):
            if len(value) > 5:
                return f"{{{len(value)} keys}}"
            return str(value)
        return str(value)[:50]
    
    def _sanitize_vars(self, vars_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive variables."""
        sensitive_keys = {"password", "token", "secret", "key", "authorization", "cookie"}
        result = {}
        for key, value in vars_dict.items():
            if key.lower() in sensitive_keys or any(s in key.lower() for s in sensitive_keys):
                result[key] = "[REDACTED]"
            else:
                result[key] = value
        return result
    
    def _get_state_vars(self, state) -> Dict[str, Any]:
        """Get state variables."""
        if hasattr(state, "__dict__"):
            return {k: v for k, v in state.__dict__.items() if not k.startswith("_")}
        if isinstance(state, dict):
            return state
        return {}
    
    def _get_app(self):
        """Get the Flaxon app instance."""
        # This would be injected by the plugin
        return None