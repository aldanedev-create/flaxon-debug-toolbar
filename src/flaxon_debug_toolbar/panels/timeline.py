"""Timeline panel for debug toolbar with Three.js 3D visualization."""

import time
import json
from typing import Dict, Any, List
from dataclasses import dataclass, field

from flaxon.http import Request, Response

from .base import Panel


@dataclass
class TimelineEvent:
    """Timeline event record."""
    name: str
    start: float
    end: float
    color: str = "#4CAF50"
    category: str = "default"


class TimelinePanel(Panel):
    """Panel displaying request timing breakdown with 3D visualization."""
    
    title = "Timeline"
    nav_title = "Timeline"
    identifier = "timeline"
    icon = "⏱️"
    order = 80
    
    has_three_scene = True
    three_scene_class = "TimelineScene"
    
    def __init__(self):
        super().__init__()
        self._events: List[TimelineEvent] = []
        self._start_time = 0
        self._end_time = 0
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        self._events = []
        self._start_time = time.time()
        
        self.add_event("Request Start", self._start_time, self._start_time)
        
        return {
            "events": [],
            "total_time": 0,
            "stages": {},
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        self._end_time = time.time()
        total_time = self._end_time - self._start_time
        
        self.add_event("Request Complete", self._end_time, self._end_time)
        
        stages = self._calculate_stages()
        
        self._data = {
            "events": self._events,
            "total_time": total_time,
            "stages": stages,
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        events = self._data.get("events", [])
        total_time = self._data.get("total_time", 0)
        total_time_ms = total_time * 1000
        stages = self._data.get("stages", {})
        
        event_data = []
        if events and len(events) > 0:
            first_start = events[0].start
            for e in events:
                event_data.append({
                    "name": e.name,
                    "start": (e.start - first_start) * 1000,
                    "end": (e.end - first_start) * 1000,
                    "color": e.color
                })
        
        event_rows = ""
        for event in events:
            duration = (event.end - event.start) * 1000
            bar_pct = (duration / total_time_ms * 100) if total_time_ms > 0 else 0
            event_rows += f"""
                <div class="event-row">
                    <span class="event-name">{event.name}</span>
                    <span class="event-duration">{duration:.2f}ms</span>
                    <div class="event-bar-container">
                        <div class="event-bar" style="width: {bar_pct:.2f}%; background: {event.color};"></div>
                    </div>
                </div>
            """
        
        stages_html = ""
        for stage, data in stages.items():
            stages_html += f"""
                <div class="stage-item">
                    <span class="stage-name">{stage}</span>
                    <span class="stage-time">{data['time']:.2f}ms</span>
                    <span class="stage-percent">{data['percent']:.1f}%</span>
                </div>
            """
        
        return f"""
        <div class="timeline-panel">
            <div class="three-container" id="timeline-three-scene">
                <canvas id="timeline-canvas"></canvas>
            </div>
            
            <div class="timeline-stats">
                <div class="stat-item">
                    <span class="stat-value">{total_time_ms:.2f}ms</span>
                    <span class="stat-label">Total Time</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{len(events)}</span>
                    <span class="stat-label">Events</span>
                </div>
            </div>
            
            <div class="stages-breakdown">
                <h4>Stage Breakdown</h4>
                <div class="stages-grid">
                    {stages_html}
                </div>
            </div>
            
            <div class="event-timeline">
                <h4>Timeline Events</h4>
                <div class="event-table">
                    <div class="event-header">
                        <span class="event-name">Event</span>
                        <span class="event-duration">Duration</span>
                        <span class="event-bar-label">Timeline</span>
                    </div>
                    {event_rows}
                </div>
            </div>
        </div>
        
        <style>
            .timeline-stats {{
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
            
            .stages-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 8px;
                margin-bottom: 16px;
                padding: 12px 16px;
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
            }}
            
            .stage-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            
            .stage-name {{
                font-weight: 600;
                font-size: 12px;
                color: var(--text-muted, #888);
            }}
            
            .stage-time {{
                font-size: 16px;
                font-weight: 700;
                color: var(--text, #e0e0e0);
            }}
            
            .stage-percent {{
                font-size: 11px;
                color: var(--text-muted, #888);
            }}
            
            .event-table {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                overflow: hidden;
                font-size: 13px;
            }}
            
            .event-header, .event-row {{
                display: flex;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .event-header {{
                font-weight: 600;
                color: var(--text-muted, #888);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: var(--bg-primary, #1a1a2e);
            }}
            
            .event-name {{ flex: 1; font-family: monospace; font-size: 12px; }}
            .event-duration {{ width: 80px; text-align: right; font-family: monospace; }}
            .event-bar-label, .event-bar-container {{ flex: 1; padding-left: 12px; }}
            
            .event-bar {{
                height: 8px;
                border-radius: 4px;
                transition: width 0.3s ease;
            }}
            
            .event-row:hover {{
                background: var(--hover, #2a2a4e);
            }}
            
            #timeline-three-scene {{
                height: 300px;
                margin-bottom: 16px;
                border-radius: 8px;
                overflow: hidden;
                background: var(--three-bg, #0d0d1a);
            }}
        </style>
        
        <script>
            (function() {{
                var container = document.getElementById('timeline-three-scene');
                var canvas = document.getElementById('timeline-canvas');
                
                if (typeof THREE !== 'undefined' && container) {{
                    var scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x0d0d1a);
                    
                    var camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
                    camera.position.set(8, 6, 10);
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
                    
                    var events = {json.dumps(event_data)};
                    
                    if (events.length > 0) {{
                        var lastEvent = events[events.length - 1];
                        var totalDuration = Math.max(lastEvent["end"] || 0, 0.001);
                        var barWidth = 0.6;
                        var spacing = 0.3;
                        
                        events.forEach(function(event, i) {{
                            var startPos = (event["start"] / totalDuration) * 6 - 3;
                            var duration = (event["end"] - event["start"]) / totalDuration * 6;
                            var height = 0.5;
                            var y = (i - events.length / 2) * (barWidth + spacing);
                            
                            var geometry = new THREE.BoxGeometry(Math.max(duration, 0.1), height, barWidth);
                            var material = new THREE.MeshStandardMaterial({{
                                color: event["color"] || 0x4CAF50,
                                metalness: 0.2,
                                roughness: 0.6,
                            }});
                            var bar = new THREE.Mesh(geometry, material);
                            bar.position.set(startPos + duration / 2, y, 0);
                            scene.add(bar);
                            
                            var dotGeo = new THREE.SphereGeometry(0.08, 8, 8);
                            var dotMat = new THREE.MeshStandardMaterial({{ color: 0xffffff }});
                            var dot = new THREE.Mesh(dotGeo, dotMat);
                            dot.position.set(startPos, y, 0);
                            scene.add(dot);
                        }});
                    }}
                    
                    var gridHelper = new THREE.GridHelper(10, 10, 0x444466, 0x222244);
                    gridHelper.position.y = -2;
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
    
    def add_event(self, name: str, start: float, end: float, color: str = "#4CAF50", category: str = "default") -> None:
        """Add a timeline event."""
        self._events.append(TimelineEvent(
            name=name,
            start=start,
            end=end,
            color=color,
            category=category,
        ))
    
    def _calculate_stages(self) -> Dict[str, Dict[str, float]]:
        """Calculate stage breakdown."""
        stages = {}
        total = self._data.get("total_time", 1) * 1000
        
        for event in self._events:
            duration = (event.end - event.start) * 1000
            if event.category not in stages:
                stages[event.category] = {"time": 0, "percent": 0}
            stages[event.category]["time"] += duration
        
        for stage in stages.values():
            stage["percent"] = (stage["time"] / total) * 100 if total > 0 else 0
        
        return stages