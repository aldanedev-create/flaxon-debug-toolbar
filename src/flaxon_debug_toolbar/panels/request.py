"""Request/response panel for debug toolbar."""

import json
from typing import Dict, Any

from flaxon.http import Request, Response

from .base import Panel


class RequestPanel(Panel):
    """Panel displaying request and response details."""
    
    title = "Request & Response"
    nav_title = "Request"
    identifier = "request"
    icon = "📨"
    order = 10
    
    has_three_scene = False
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        scope = request.scope
        scheme = scope.get("scheme", "http")
        host = request.headers.get("host", "")
        query_string = scope.get("query_string", b"")
        if isinstance(query_string, bytes):
            query_string = query_string.decode("latin-1")
        url = f"{scheme}://{host}{request.path}"
        if query_string:
            url += f"?{query_string}"
        client = scope.get("client")

        return {
            "method": request.method,
            "path": request.path,
            "url": url,
            "query": dict(request.query_params),
            "headers": self._sanitize_headers(dict(request.headers)),
            "client_ip": client[0] if client else None,
            "body_preview": await self._get_body_preview(request),
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        if not response:
            return
        
        self._data.update({
            "status_code": response.status_code,
            "status_text": self._get_status_text(response.status_code),
            "response_headers": self._sanitize_headers(response.headers),
            "response_body_size": len(response.content) if response.content else 0,
            "response_body_preview": self._truncate_body(
                response.content.decode("utf-8", errors="ignore") if response.content else ""
            ),
        })
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        data = {**self._data, **context}
        
        return f"""
        <div class="request-panel">
            <div class="request-summary">
                <div class="request-method {data.get('method', '').lower()}">
                    {data.get('method', 'GET')}
                </div>
                <div class="request-path">
                    {data.get('path', '/')}
                </div>
                <div class="request-status status-{data.get('status_code', 200)}">
                    {data.get('status_code', 200)} {data.get('status_text', 'OK')}
                </div>
            </div>
            
            <div class="request-details">
                <div class="detail-section">
                    <h4>Request</h4>
                    <div class="detail-row">
                        <span class="label">URL:</span>
                        <span class="value">{data.get('url', '')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Client IP:</span>
                        <span class="value">{data.get('client_ip', 'unknown')}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Headers</h4>
                    <div class="headers-table">
                        {self._render_headers(data.get('headers', {}))}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Query Parameters</h4>
                    <div class="query-table">
                        {self._render_query(data.get('query', {}))}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Request Body</h4>
                    <pre class="body-preview">{data.get('body_preview', '')}</pre>
                </div>
                
                <div class="detail-section">
                    <h4>Response</h4>
                    <div class="detail-row">
                        <span class="label">Status:</span>
                        <span class="value">{data.get('status_code', 200)} {data.get('status_text', 'OK')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Body Size:</span>
                        <span class="value">{data.get('response_body_size', 0)} bytes</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Response Headers</h4>
                    <div class="headers-table">
                        {self._render_headers(data.get('response_headers', {}))}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Response Body Preview</h4>
                    <pre class="body-preview">{data.get('response_body_preview', '')}</pre>
                </div>
            </div>
        </div>
        
        <style>
            .request-summary {{
                display: flex;
                align-items: center;
                gap: 16px;
                padding: 12px 16px;
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                margin-bottom: 16px;
            }}
            
            .request-method {{
                font-weight: 700;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 14px;
            }}
            
            .request-method.get {{ color: #4CAF50; }}
            .request-method.post {{ color: #FF9800; }}
            .request-method.put {{ color: #2196F3; }}
            .request-method.delete {{ color: #f44336; }}
            .request-method.patch {{ color: #9C27B0; }}
            
            .request-path {{
                font-family: monospace;
                font-size: 14px;
                flex: 1;
            }}
            
            .request-status {{
                font-weight: 600;
                padding: 4px 12px;
                border-radius: 4px;
            }}
            
            .status-200 {{ color: #4CAF50; }}
            .status-201 {{ color: #4CAF50; }}
            .status-301 {{ color: #FF9800; }}
            .status-302 {{ color: #FF9800; }}
            .status-400 {{ color: #FF9800; }}
            .status-401 {{ color: #FF9800; }}
            .status-403 {{ color: #FF9800; }}
            .status-404 {{ color: #FF9800; }}
            .status-500 {{ color: #f44336; }}
            
            .detail-section {{
                margin-bottom: 20px;
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                padding: 12px 16px;
            }}
            
            .detail-section h4 {{
                margin: 0 0 8px 0;
                font-size: 13px;
                text-transform: uppercase;
                color: var(--text-muted, #888);
                letter-spacing: 0.5px;
            }}
            
            .detail-row {{
                display: flex;
                padding: 4px 0;
                font-size: 13px;
            }}
            
            .detail-row .label {{
                font-weight: 500;
                min-width: 120px;
                color: var(--text-muted, #888);
            }}
            
            .detail-row .value {{
                font-family: monospace;
            }}
            
            .headers-table, .query-table {{
                font-family: monospace;
                font-size: 12px;
                overflow-x: auto;
            }}
            
            .headers-table .header-row, .query-table .query-row {{
                display: flex;
                padding: 2px 0;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .headers-table .header-key, .query-table .query-key {{
                min-width: 200px;
                font-weight: 500;
                color: var(--text-muted, #888);
            }}
            
            .headers-table .header-value, .query-table .query-value {{
                flex: 1;
                word-break: break-all;
            }}
            
            .body-preview {{
                background: var(--bg-primary, #1a1a2e);
                padding: 12px;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 12px;
                max-height: 200px;
                overflow-y: auto;
                margin: 0;
            }}
        </style>
        """
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize headers by redacting sensitive values."""
        sensitive = {"authorization", "cookie", "x-api-key", "x-auth-token", "set-cookie"}
        return {
            k: "[REDACTED]" if k.lower() in sensitive else v
            for k, v in headers.items()
        }
    
    def _render_headers(self, headers: Dict[str, str]) -> str:
        """Render headers as HTML."""
        if not headers:
            return "<div class='empty'>No headers</div>"
        
        rows = []
        for key, value in headers.items():
            rows.append(f"""
                <div class="header-row">
                    <span class="header-key">{key}</span>
                    <span class="header-value">{value}</span>
                </div>
            """)
        return "".join(rows)
    
    def _render_query(self, query: Dict[str, str]) -> str:
        """Render query parameters as HTML."""
        if not query:
            return "<div class='empty'>No query parameters</div>"
        
        rows = []
        for key, value in query.items():
            rows.append(f"""
                <div class="query-row">
                    <span class="query-key">{key}</span>
                    <span class="query-value">{value}</span>
                </div>
            """)
        return "".join(rows)
    
    async def _get_body_preview(self, request: Request) -> str:
        """Get truncated body preview."""
        try:
            body = await request.body()
            if body:
                text = body.decode("utf-8", errors="ignore")
                return self._truncate_body(text)
        except Exception:
            pass
        return ""
    
    def _truncate_body(self, body: str, max_length: int = 500) -> str:
        """Truncate body to max length."""
        if len(body) > max_length:
            return body[:max_length] + "... (truncated)"
        return body
    
    def _get_status_text(self, status: int) -> str:
        """Get HTTP status text."""
        status_texts = {
            200: "OK",
            201: "Created",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            304: "Not Modified",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Unprocessable Entity",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
        }
        return status_texts.get(status, "Unknown")