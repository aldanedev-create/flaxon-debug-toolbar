"""Logging panel for debug toolbar."""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field
import time

from flaxon.http import Request, Response

from .base import Panel


@dataclass
class LogEntry:
    """Log entry record."""
    level: str
    message: str
    logger: str
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)


class LoggingPanel(Panel):
    """Panel displaying log messages."""
    
    title = "Logging"
    nav_title = "Logs"
    identifier = "logging"
    icon = "📝"
    order = 40
    
    has_three_scene = False
    
    def __init__(self):
        super().__init__()
        self._logs: List[LogEntry] = []
        self._original_handler = None
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        self._logs = []
        
        # Capture logs
        self._setup_log_capture()
        
        return {
            "logs": [],
            "count": 0,
            "error_count": 0,
            "warning_count": 0,
        }
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        self._restore_log_capture()
        
        error_count = sum(1 for log in self._logs if log.level == "ERROR")
        warning_count = sum(1 for log in self._logs if log.level == "WARNING")
        
        self._data = {
            "logs": self._logs,
            "count": len(self._logs),
            "error_count": error_count,
            "warning_count": warning_count,
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        logs = self._data.get("logs", [])
        count = self._data.get("count", 0)
        error_count = self._data.get("error_count", 0)
        warning_count = self._data.get("warning_count", 0)
        
        # Build log rows
        log_rows = ""
        for log in logs:
            level_class = log.level.lower()
            log_rows += f"""
                <div class="log-row level-{level_class}">
                    <span class="log-level">{log.level}</span>
                    <span class="log-time">{time.strftime('%H:%M:%S', time.localtime(log.timestamp))}</span>
                    <span class="log-logger">{log.logger}</span>
                    <span class="log-message">{log.message}</span>
                </div>
            """
        
        return f"""
        <div class="logging-panel">
            <!-- Statistics -->
            <div class="log-stats">
                <div class="stat-item">
                    <span class="stat-value">{count}</span>
                    <span class="stat-label">Total Logs</span>
                </div>
                <div class="stat-item stat-error">
                    <span class="stat-value">{error_count}</span>
                    <span class="stat-label">Errors</span>
                </div>
                <div class="stat-item stat-warning">
                    <span class="stat-value">{warning_count}</span>
                    <span class="stat-label">Warnings</span>
                </div>
            </div>
            
            <!-- Log List -->
            <div class="log-list">
                <h4>Log Messages</h4>
                <div class="log-table">
                    <div class="log-header">
                        <span class="log-level">Level</span>
                        <span class="log-time">Time</span>
                        <span class="log-logger">Logger</span>
                        <span class="log-message">Message</span>
                    </div>
                    {log_rows}
                </div>
            </div>
        </div>
        
        <style>
            .log-stats {{
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
            
            .stat-item.stat-error .stat-value {{ color: #f44336; }}
            .stat-item.stat-warning .stat-value {{ color: #FF9800; }}
            
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
            
            .log-table {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                overflow: hidden;
                font-size: 13px;
            }}
            
            .log-header, .log-row {{
                display: flex;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .log-header {{
                font-weight: 600;
                color: var(--text-muted, #888);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: var(--bg-primary, #1a1a2e);
            }}
            
            .log-level {{ width: 80px; font-weight: 600; text-transform: uppercase; font-size: 11px; }}
            .log-time {{ width: 80px; font-family: monospace; font-size: 12px; }}
            .log-logger {{ width: 150px; font-size: 12px; color: var(--text-muted, #888); }}
            .log-message {{ flex: 1; font-family: monospace; font-size: 12px; }}
            
            .level-debug .log-level {{ color: #888; }}
            .level-info .log-level {{ color: #4CAF50; }}
            .level-warning .log-level {{ color: #FF9800; }}
            .level-error .log-level {{ color: #f44336; }}
            .level-critical .log-level {{ color: #d32f2f; font-weight: 700; }}
            
            .log-row:hover {{
                background: var(--hover, #2a2a4e);
            }}
        </style>
        """
    
    def _setup_log_capture(self) -> None:
        """Set up log capture."""
        class CaptureHandler(logging.Handler):
            def __init__(self, panel):
                self.panel = panel
                super().__init__()
            
            def emit(self, record):
                self.panel._logs.append(LogEntry(
                    level=record.levelname,
                    message=record.getMessage(),
                    logger=record.name,
                    timestamp=record.created,
                ))
        
        handler = CaptureHandler(self)
        handler.setLevel(logging.DEBUG)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        self._original_handler = handler
    
    def _restore_log_capture(self) -> None:
        """Restore log capture."""
        if self._original_handler:
            root_logger = logging.getLogger()
            root_logger.removeHandler(self._original_handler)
            self._original_handler = None