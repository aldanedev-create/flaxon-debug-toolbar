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
    operation: str
    result: str
    value: Any = None
    timestamp: float = field(default_factory=time.time)
    time: float = 0.0

class CachePanel(Panel):
    """Panel displaying cache operations."""
    
    title = "Cache"
    nav_title = "Cache"
    identifier = "cache"
    icon = "💾"
    order = 30
    
    has_three_scene = True
    three_scene_class = "CacheScene"
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data with thread-safe container."""
        return {
            "operations": [],
            "hits": 0,
            "misses": 0,
            "total": 0,
            "hit_rate": 0.0,
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        panel_data = data.get("panels", {}).get(self.identifier, {})
        operations = panel_data.get("operations", [])
        hits = panel_data.get("hits", 0)
        misses = panel_data.get("misses", 0)
        
        total = len(operations)
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        self._data = {
            "operations": operations,
            "hits": hits,
            "misses": misses,
            "total": total,
            "hit_rate": hit_rate,
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML safely."""
        operations = context.get("operations", [])
        hits = context.get("hits", 0)
        misses = context.get("misses", 0)
        total = context.get("total", 0)
        hit_rate = context.get("hit_rate", 0.0)
        
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
        """