"""Middleware panel for debug toolbar."""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from flaxon.http import Request, Response

from .base import Panel


@dataclass
class MiddlewareExecution:
    """Middleware execution record."""
    name: str
    order: int
    type: str  # "request", "response", or "both"
    time: float = 0.0
    success: bool = True
    error: Optional[str] = None


class MiddlewarePanel(Panel):
    """Panel displaying middleware execution order and timing."""
    
    title = "Middleware"
    nav_title = "Middleware"
    identifier = "middleware"
    icon = "🔗"
    order = 60
    
    has_three_scene = True
    three_scene_class = "MiddlewareScene"
    
    def __init__(self):
        super().__init__()
        self._executions: List[MiddlewareExecution] = []
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        self._executions = []
        
        return {
            "executions": [],
            "count": 0,
            "total_time": 0,
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        total_time = sum(e.time for e in self._executions)
        
        self._data = {
            "executions": self._executions,
            "count": len(self._executions),
            "total_time": total_time,
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        executions = self._data.get("executions", [])
        count = self._data.get("count", 0)
        total_time = self._data.get("total_time", 0)
        
        # Build execution rows
        exec_rows = ""
        for exec in executions:
            type_class = exec.type.lower()
            status_class = "success" if exec.success else "error"
            exec_rows += f"""
                <div class="exec-row type-{type_class} status-{status_class}">
                    <span class="exec-order">#{exec.order}</span>
                    <span class="exec-name">{exec.name}</span>
                    <span class="exec-type">{exec.type}</span>
                    <span class="exec-time">{exec.time:.2f}ms</span>
                    <span class="exec-status">{'✅' if exec.success else '❌'}</span>
                </div>
            """
        
        return f"""
        <div class="middleware-panel">
            <!-- Three.js 3D Visualization -->
            <div class="three-container" id="middleware-three-scene">
                <canvas id="middleware-canvas"></canvas>
            </div>
            
            <!-- Statistics -->
            <div class="middleware-stats">
                <div class="stat-item">
                    <span class="stat-value">{count}</span>
                    <span class="stat-label">Total Middleware</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{total_time:.2f}ms</span>
                    <span class="stat-label">Total Time</span>
                </div>
            </div>
            
            <!-- Execution List -->
            <div class="execution-list">
                <h4>Middleware Execution Order</h4>
                <div class="execution-table">
                    <div class="exec-header">
                        <span class="exec-order">#</span>
                        <span class="exec-name">Middleware</span>
                        <span class="exec-type">Type</span>
                        <span class="exec-time">Time</span>
                        <span class="exec-status">Status</span>
                    </div>
                    {exec_rows}
                </div>
            </div>
        </div>
        
        <style>
            .middleware-stats {{
                display: flex;
                gap: 20px;
                margin-bottom: 16px;
                padding: 12px 16px;
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
            }}
            
            .stat-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            
            .stat-value {{
                font-size: 20px;
                font-weight: 700;
                color: var(--text, #e0e0e0);
            }}
            
            .stat-label {{
                font-size: 11px;
                text-transform: uppercase;
                color: var(--text-muted, #888);
                letter-spacing: 0.5px;
            }}
            
            .execution-table {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                overflow: hidden;
                font-size: 13px;
            }}
            
            .exec-header, .exec-row {{
                display: flex;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .exec-header {{
                font-weight: 600;
                color: var(--text-muted, #888);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: var(--bg-primary, #1a1a2e);
            }}
            
            .exec-order {{ width: 40px; font-family: monospace; font-size: 12px; }}
            .exec-name {{ flex: 1; font-family: monospace; font-size: 12px; }}
            .exec-type {{ width: 80px; text-transform: uppercase; font-size: 11px; }}
            .exec-time {{ width: 80px; text-align: right; font-family: monospace; }}
            .exec-status {{ width: 40px; text-align: center; }}
            
            .type-request .exec-type {{ color: #2196F3; }}
            .type-response .exec-type {{ color: #4CAF50; }}
            .type-both .exec-type {{ color: #9C27B0; }}
            
            .status-success .exec-status {{ color: #4CAF50; }}
            .status-error .exec-status {{ color: #f44336; }}
            
            .exec-row:hover {{
                background: var(--hover, #2a2a4e);
            }}
            
            #middleware-three-scene {{
                height: 250px;
                margin-bottom: 16px;
                border-radius: 8px;
                overflow: hidden;
                background: var(--three-bg, #0d0d1a);
            }}
        </style>
        """
    
    def add_execution(self, name: str, order: int, exec_type: str, time: float = 0.0, success: bool = True, error: str = None) -> None:
        """Add a middleware execution record."""
        self._executions.append(MiddlewareExecution(
            name=name,
            order=order,
            type=exec_type,
            time=time,
            success=success,
            error=error,
        ))