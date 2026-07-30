"""Cache panel for debug toolbar."""

from typing import Dict, Any, List
from dataclasses import dataclass, field
import time

from flaxon.http import Request, Response

from .base import Panel


@dataclass
class CacheOperation:
    """Cache operation record."""
    key: str
    operation: str  # GET, SET, DELETE, CLEAR
    result: str  # HIT, MISS, SUCCESS, FAIL
    value: Any = None
    time: float = 0.0
    timestamp: float = field(default_factory=time.time)


class CachePanel(Panel):
    """Panel displaying cache operations."""
    
    title = "Cache"
    nav_title = "Cache"
    identifier = "cache"
    icon = "💾"
    order = 30
    
    has_three_scene = True
    three_scene_class = "CacheScene"
    
    def __init__(self):
        super().__init__()
        self._operations: List[CacheOperation] = []
        self._hits = 0
        self._misses = 0
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        self._operations = []
        self._hits = 0
        self._misses = 0
        
        return {
            "operations": [],
            "hits": 0,
            "misses": 0,
            "total": 0,
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        total = len(self._operations)
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        self._data = {
            "operations": self._operations,
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": hit_rate,
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        operations = self._data.get("operations", [])
        hits = self._data.get("hits", 0)
        misses = self._data.get("misses", 0)
        total = self._data.get("total", 0)
        hit_rate = self._data.get("hit_rate", 0)
        
        # Build operation rows
        operation_rows = ""
        for op in operations:
            result_class = "hit" if op.result == "HIT" else "miss" if op.result == "MISS" else "success" if op.result == "SUCCESS" else "fail"
            operation_rows += f"""
                <div class="operation-row result-{result_class}">
                    <span class="op-key">{op.key}</span>
                    <span class="op-operation">{op.operation}</span>
                    <span class="op-result">{op.result}</span>
                    <span class="op-time">{op.time:.2f}ms</span>
                </div>
            """
        
        return f"""
        <div class="cache-panel">
            <!-- Three.js 3D Visualization -->
            <div class="three-container" id="cache-three-scene">
                <canvas id="cache-canvas"></canvas>
            </div>
            
            <!-- Statistics -->
            <div class="cache-stats">
                <div class="stat-item">
                    <span class="stat-value">{total}</span>
                    <span class="stat-label">Total Operations</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{hits}</span>
                    <span class="stat-label">Hits</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{misses}</span>
                    <span class="stat-label">Misses</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{hit_rate:.1f}%</span>
                    <span class="stat-label">Hit Rate</span>
                </div>
            </div>
            
            <!-- Operations List -->
            <div class="operation-list">
                <h4>Cache Operations</h4>
                <div class="operation-table">
                    <div class="operation-header">
                        <span class="op-key">Key</span>
                        <span class="op-operation">Operation</span>
                        <span class="op-result">Result</span>
                        <span class="op-time">Time</span>
                    </div>
                    {operation_rows}
                </div>
            </div>
        </div>
        
        <style>
            .cache-stats {{
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
            
            .operation-table {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                overflow: hidden;
                font-size: 13px;
            }}
            
            .operation-header, .operation-row {{
                display: flex;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .operation-header {{
                font-weight: 600;
                color: var(--text-muted, #888);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: var(--bg-primary, #1a1a2e);
            }}
            
            .op-key {{ flex: 1; font-family: monospace; font-size: 12px; }}
            .op-operation {{ width: 80px; text-transform: uppercase; font-size: 11px; }}
            .op-result {{ width: 70px; font-weight: 600; }}
            .op-time {{ width: 80px; text-align: right; font-family: monospace; }}
            
            .result-hit .op-result {{ color: #4CAF50; }}
            .result-miss .op-result {{ color: #f44336; }}
            .result-success .op-result {{ color: #4CAF50; }}
            .result-fail .op-result {{ color: #f44336; }}
            
            .operation-row:hover {{
                background: var(--hover, #2a2a4e);
                cursor: pointer;
            }}
            
            #cache-three-scene {{
                height: 250px;
                margin-bottom: 16px;
                border-radius: 8px;
                overflow: hidden;
                background: var(--three-bg, #0d0d1a);
            }}
        </style>
        """
    
    def add_operation(self, key: str, operation: str, result: str, value: Any = None, time: float = 0.0) -> None:
        """Add a cache operation."""
        self._operations.append(CacheOperation(
            key=key,
            operation=operation,
            result=result,
            value=value,
            time=time,
        ))
        
        if result == "HIT":
            self._hits += 1
        elif result == "MISS":
            self._misses += 1