"""SQL queries panel for debug toolbar with Three.js 3D visualization."""

import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from flaxon.http import Request, Response

from .base import Panel


@dataclass
class SQLQuery:
    """SQL query record."""
    sql: str
    parameters: List[Any] = field(default_factory=list)
    time: float = 0.0
    type: str = "SELECT"
    success: bool = True
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class SQLPanel(Panel):
    """Panel displaying SQL queries with Three.js 3D visualization."""
    
    title = "SQL Queries"
    nav_title = "SQL"
    identifier = "sql"
    icon = "🗄️"
    order = 20
    
    has_three_scene = True
    three_scene_class = "SQLScene"
    
    def __init__(self):
        super().__init__()
        self._queries: List[SQLQuery] = []
        self._slow_threshold = 100  # milliseconds
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        self._queries = []
        
        return {
            "queries": [],
            "count": 0,
            "total_time": 0,
            "slow_queries": 0,
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        total_time = sum(q.time for q in self._queries)
        slow_queries = [q for q in self._queries if q.time > self._slow_threshold]
        
        self._data = {
            "queries": self._queries,
            "count": len(self._queries),
            "total_time": total_time,
            "slow_queries": len(slow_queries),
            "slow_threshold": self._slow_threshold,
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        queries = self._data.get("queries", [])
        total_time = self._data.get("total_time", 0)
        count = self._data.get("count", 0)
        slow_count = self._data.get("slow_queries", 0)
        slow_threshold = self._data.get("slow_threshold", 100)
        
        query_rows = ""
        for i, query in enumerate(queries):
            time_class = "slow" if query.time > slow_threshold else "normal"
            query_rows += f"""
                <div class="query-row {time_class}">
                    <div class="query-number">#{i + 1}</div>
                    <div class="query-type">{query.type}</div>
                    <div class="query-sql">{self._highlight_sql(query.sql)}</div>
                    <div class="query-time">{query.time:.2f}ms</div>
                    <div class="query-status">{'✅' if query.success else '❌'}</div>
                </div>
            """
        
        query_data = []
        for q in queries[:20]:
            query_data.append({
                "sql": q.sql[:50] + "..." if len(q.sql) > 50 else q.sql,
                "time": q.time,
                "type": q.type,
                "success": q.success
            })
        
        return f"""
        <div class="sql-panel">
            <div class="three-container" id="sql-three-scene">
                <canvas id="sql-canvas"></canvas>
            </div>
            
            <div class="sql-stats">
                <div class="stat-item">
                    <span class="stat-value">{count}</span>
                    <span class="stat-label">Total Queries</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{total_time:.2f}ms</span>
                    <span class="stat-label">Total Time</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{slow_count}</span>
                    <span class="stat-label">Slow Queries</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{slow_threshold}ms</span>
                    <span class="stat-label">Slow Threshold</span>
                </div>
            </div>
            
            <div class="query-list">
                <h4>Queries</h4>
                <div class="query-table">
                    <div class="query-header">
                        <span class="query-number">#</span>
                        <span class="query-type">Type</span>
                        <span class="query-sql">SQL</span>
                        <span class="query-time">Time</span>
                        <span class="query-status">Status</span>
                    </div>
                    {query_rows}
                </div>
            </div>
        </div>
        
        <style>
            .sql-stats {{
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
            
            .query-table {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                overflow: hidden;
                font-size: 13px;
            }}
            
            .query-header, .query-row {{
                display: flex;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .query-header {{
                font-weight: 600;
                color: var(--text-muted, #888);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: var(--bg-primary, #1a1a2e);
            }}
            
            .query-number {{ width: 40px; }}
            .query-type {{ width: 70px; font-size: 11px; text-transform: uppercase; }}
            .query-sql {{ flex: 1; font-family: monospace; font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
            .query-time {{ width: 80px; text-align: right; font-family: monospace; }}
            .query-status {{ width: 40px; text-align: center; }}
            
            .query-row.slow .query-time {{ color: #f44336; font-weight: 600; }}
            .query-row.normal .query-time {{ color: #4CAF50; }}
            
            .query-row:hover {{
                background: var(--hover, #2a2a4e);
                cursor: pointer;
            }}
            
            .query-type.select {{ color: #4CAF50; }}
            .query-type.insert {{ color: #FF9800; }}
            .query-type.update {{ color: #2196F3; }}
            .query-type.delete {{ color: #f44336; }}
            
            #sql-three-scene {{
                height: 300px;
                margin-bottom: 16px;
                border-radius: 8px;
                overflow: hidden;
                background: var(--three-bg, #0d0d1a);
            }}
        </style>
        
        <script>
            (function() {{
                var container = document.getElementById('sql-three-scene');
                var canvas = document.getElementById('sql-canvas');
                
                if (typeof THREE !== 'undefined' && container) {{
                    var scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x0d0d1a);
                    
                    var camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
                    camera.position.set(10, 8, 12);
                    camera.lookAt(0, 0, 0);
                    
                    var renderer = new THREE.WebGLRenderer({{
                        canvas: canvas,
                        antialias: true,
                    }});
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                    
                    var ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                    scene.add(ambientLight);
                    
                    var directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    directionalLight.position.set(10, 20, 10);
                    scene.add(directionalLight);
                    
                    var queries = {json.dumps(query_data)};
                    
                    var maxTime = Math.max.apply(null, queries.map(function(q) {{ return q.time; }})) || 1;
                    var barWidth = 0.8;
                    var spacing = 0.4;
                    var totalWidth = queries.length * (barWidth + spacing);
                    var startX = -totalWidth / 2 + barWidth / 2;
                    
                    var colors = {{
                        'SELECT': 0x4CAF50,
                        'INSERT': 0xFF9800,
                        'UPDATE': 0x2196F3,
                        'DELETE': 0xf44336,
                    }};
                    
                    queries.forEach(function(query, i) {{
                        var height = (query.time / maxTime) * 3;
                        var x = startX + i * (barWidth + spacing);
                        var y = height / 2;
                        
                        var color = colors[query.type] || 0x888888;
                        
                        var geometry = new THREE.BoxGeometry(barWidth, height, barWidth);
                        var material = new THREE.MeshStandardMaterial({{
                            color: color,
                            metalness: 0.3,
                            roughness: 0.4,
                        }});
                        var bar = new THREE.Mesh(geometry, material);
                        bar.position.set(x, y, 0);
                        scene.add(bar);
                    }});
                    
                    var gridHelper = new THREE.GridHelper(10, 10, 0x444466, 0x222244);
                    gridHelper.position.y = 0;
                    scene.add(gridHelper);
                    
                    function animate() {{
                        requestAnimationFrame(animate);
                        renderer.render(scene, camera);
                    }}
                    animate();
                    
                    window.addEventListener('resize', function() {{
                        var width = container.clientWidth;
                        var height = container.clientHeight;
                        camera.aspect = width / height;
                        camera.updateProjectionMatrix();
                        renderer.setSize(width, height);
                    }});
                }}
            }})();
        </script>
        """
    
    def _highlight_sql(self, sql: str) -> str:
        """Simple SQL syntax highlighting."""
        keywords = ["SELECT", "FROM", "WHERE", "JOIN", "INSERT", "UPDATE", "DELETE", 
                   "CREATE", "ALTER", "DROP", "TABLE", "INDEX", "VIEW", "ORDER BY",
                   "GROUP BY", "HAVING", "LIMIT", "OFFSET", "AND", "OR", "NOT",
                   "INNER", "LEFT", "RIGHT", "OUTER", "FULL", "CROSS", "UNION"]
        
        for keyword in keywords:
            sql = sql.replace(keyword, f'<span class="sql-keyword">{keyword}</span>')
        
        return sql
    
    def add_query(self, sql: str, parameters: List[Any] = None, time: float = 0.0) -> None:
        """Add a query to the panel."""
        query_type = sql.strip().split()[0].upper() if sql else "UNKNOWN"
        self._queries.append(SQLQuery(
            sql=sql,
            parameters=parameters or [],
            time=time,
            type=query_type,
        ))