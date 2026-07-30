"""Templates panel for debug toolbar."""

import time
from typing import Dict, Any, List
from dataclasses import dataclass, field

from flaxon.http import Request, Response

from .base import Panel


@dataclass
class TemplateRender:
    """Template render record."""
    name: str
    context: Dict[str, Any] = field(default_factory=dict)
    time: float = 0.0
    type: str = "jinja2"


class TemplatesPanel(Panel):
    """Panel displaying template rendering information."""
    
    title = "Templates"
    nav_title = "Templates"
    identifier = "templates"
    icon = "📄"
    order = 70
    
    has_three_scene = False
    
    def __init__(self):
        super().__init__()
        self._templates: List[TemplateRender] = []
    
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request data."""
        self._templates = []
        return {"templates": [], "count": 0}
    
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """Process response data."""
        self._data = {
            "templates": self._templates,
            "count": len(self._templates),
        }
    
    async def render(self, context: Dict[str, Any]) -> str:
        """Render panel HTML."""
        templates = self._data.get("templates", [])
        count = self._data.get("count", 0)
        
        # Build template rows
        template_rows = ""
        for i, template in enumerate(templates):
            template_rows += f"""
                <div class="template-row">
                    <span class="template-number">#{i + 1}</span>
                    <span class="template-name">{template.name}</span>
                    <span class="template-type">{template.type}</span>
                    <span class="template-time">{template.time:.2f}ms</span>
                </div>
            """
        
        return f"""
        <div class="templates-panel">
            <!-- Statistics -->
            <div class="template-stats">
                <div class="stat-item">
                    <span class="stat-value">{count}</span>
                    <span class="stat-label">Templates Rendered</span>
                </div>
            </div>
            
            <!-- Template List -->
            <div class="template-list">
                <h4>Rendered Templates</h4>
                <div class="template-table">
                    <div class="template-header">
                        <span class="template-number">#</span>
                        <span class="template-name">Template</span>
                        <span class="template-type">Type</span>
                        <span class="template-time">Time</span>
                    </div>
                    {template_rows}
                </div>
            </div>
            
            <!-- Template Context (expandable) -->
            <div class="template-context" style="display:none;">
                <h4>Template Context</h4>
                <pre class="context-preview"></pre>
            </div>
        </div>
        
        <style>
            .template-stats {{
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
            
            .template-table {{
                background: var(--bg-secondary, #2a2a4e);
                border-radius: 8px;
                overflow: hidden;
                font-size: 13px;
            }}
            
            .template-header, .template-row {{
                display: flex;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid var(--border, #2a2a3e);
            }}
            
            .template-header {{
                font-weight: 600;
                color: var(--text-muted, #888);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: var(--bg-primary, #1a1a2e);
            }}
            
            .template-number {{ width: 40px; font-family: monospace; font-size: 12px; }}
            .template-name {{ flex: 1; font-family: monospace; font-size: 12px; }}
            .template-type {{ width: 80px; text-transform: uppercase; font-size: 11px; }}
            .template-time {{ width: 80px; text-align: right; font-family: monospace; }}
            
            .template-row:hover {{
                background: var(--hover, #2a2a4e);
                cursor: pointer;
            }}
            
            .context-preview {{
                background: var(--bg-primary, #1a1a2e);
                padding: 12px;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 12px;
                max-height: 200px;
                overflow-y: auto;
                margin: 8px 0;
            }}
        </style>
        """
    
    def add_template(self, name: str, context: Dict[str, Any] = None, time: float = 0.0, type: str = "jinja2") -> None:
        """Add a template render record."""
        self._templates.append(TemplateRender(
            name=name,
            context=context or {},
            time=time,
            type=type,
        ))