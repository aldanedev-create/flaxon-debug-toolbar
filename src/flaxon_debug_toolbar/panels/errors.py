"""Errors panel for debug toolbar with Three.js 3D visualization."""

import traceback
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import time

from flaxon.http import Request, Response

from .base import Panel


@dataclass
class ErrorRecord:
    """Error record."""
    type: str
    message: str
    traceback: str
    timestamp: float = field(default_factory=time.time)
    severity: str = "error"  # "error", "warning", "critical"
    context: Dict[str, Any] = field(default_factory=dict)


class ErrorsPanel(Panel):
    """Panel displaying errors and exceptions with 3D visualization."""
    
    title = "Errors"
    nav_title = "Errors"
    identifier = "errors"
    icon = "❌"
    order = 100
    
    has_three_scene = True
    three_scene_class = "ErrorsScene"
    
    def __init__(self):
        super().__init__()
        self._errors: List[ErrorRecord] = []
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        self._errors = []
        return {"errors": [], "count": 0, "critical_count": 0}
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        critical_count = sum(1 for e in self._errors if e.severity == "critical")
        
        self._data = {
            "errors": self._errors,
            "count": len(self._errors),
            "critical_count": critical_count,
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        errors = self._data.get("errors", [])
        count = self._data.get("count", 0)
        critical_count = self._data.get("critical_count", 0)
        
        # Build error rows
        error_rows = ""
        for error in errors:
            severity_class = error.severity
            error_rows += f"""
                <div class="error-row severity-{severity_class}">
                    <span class="error-severity">{error.severity.upper()}</span>
                    <span class="error-type">{error.type}</span>
                    <span class="error-message">{error.message}</span>
                    <span class="error-time">{time.strftime('%H:%M:%S', time.localtime(error.timestamp))}</span>
                </div>
            """
        
        return f"""
        <div class="errors-panel">
            <!-- Three.js 3D Visualization -->
            <div class="three-container" id="errors-three-scene">
                <canvas id="errors-canvas"></canvas>
            </div>
            
            <!-- Statistics -->
            <div class="error-stats">
                <div class="stat-item">
                    <span class="stat-value">{count}</span>
                    <span class="stat-label">Total Errors</span>
                </div>
                <div class="stat-item stat-critical">
                    <span class="stat-value">{critical_count}</span>
                    <span class="stat-label">Critical</span>
                </div>
            </div>
            
            <!-- Error List -->
            <div class="error-list">
                <h4>Errors</h4>
                <div class="error-table">
                    <div class="error-header">
                        <span class="error-severity">Severity</span>
                        <span class="error-type">Type</span>
                        <span class="error-message">Message</span>
                        <span class="error-time">Time</span>
                    </div>
                    {error_rows}
                </div>
            </div>
            
            <!-- Error Details (expandable) -->
            <div class="error-details" style="display:none;">
                <h4>Error Details</h4>
                <pre class="traceback-display"></pre>
            </div>
        </div>
        
        <style>
            .error-stats {{
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
            
            .stat-item.stat-critical .stat-value {{ color: #f44336; }}
            
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
            
            .error-table {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                overflow: hidden;
                font-size: 13px;
            }}
            
            .error-header, .error-row {{
                display: flex;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .error-header {{
                font-weight: 600;
                color: var(--text-muted, #888);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: var(--bg-primary, #1a1a2e);
            }}
            
            .error-severity {{ width: 80px; font-weight: 600; font-size: 11px; text-transform: uppercase; }}
            .error-type {{ width: 120px; font-family: monospace; font-size: 12px; }}
            .error-message {{ flex: 1; font-family: monospace; font-size: 12px; }}
            .error-time {{ width: 80px; font-family: monospace; font-size: 12px; text-align: right; }}
            
            .severity-error .error-severity {{ color: #f44336; }}
            .severity-warning .error-severity {{ color: #FF9800; }}
            .severity-critical .error-severity {{ color: #d32f2f; font-weight: 700; }}
            
            .error-row:hover {{
                background: var(--hover, #2a2a4e);
                cursor: pointer;
            }}
            
            .traceback-display {{
                background: var(--bg-primary, #1a1a2e);
                padding: 12px;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 12px;
                max-height: 300px;
                overflow-y: auto;
                margin: 8px 0;
                white-space: pre-wrap;
                font-family: monospace;
                color: #e0e0e0;
            }}
            
            #errors-three-scene {{
                height: 250px;
                margin-bottom: 16px;
                border-radius: 8px;
                overflow: hidden;
                background: var(--three-bg, #0d0d1a);
            }}
        </style>
        """
    
    def add_error(self, error_type: str, message: str, traceback_str: str = "", severity: str = "error", context: Dict[str, Any] = None) -> None:
        """Add an error record."""
        self._errors.append(ErrorRecord(
            type=error_type,
            message=message,
            traceback=traceback_str,
            severity=severity,
            context=context or {},
        ))
    
    def add_exception(self, exc: Exception, context: Dict[str, Any] = None) -> None:
        """Add an exception record."""
        traceback_str = traceback.format_exc()
        severity = "critical" if isinstance(exc, (SystemExit, KeyboardInterrupt)) else "error"
        self.add_error(
            error_type=exc.__class__.__name__,
            message=str(exc),
            traceback=traceback_str,
            severity=severity,
            context=context,
        )