"""Debug toolbar plugin for Flaxon with Three.js 3D visualizations."""

import os
import time
import json
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field

from flaxon import Flaxon
from flaxon.plugin import Plugin
from flaxon.http import Request, Response

from .middleware import DebugToolbarMiddleware
from .panels.base import Panel
from .panels.request import RequestPanel
from .panels.sql import SQLPanel
from .panels.cache import CachePanel
from .panels.logging import LoggingPanel
from .panels.routing import RoutingPanel
from .panels.middleware import MiddlewarePanel
from .panels.templates import TemplatesPanel
from .panels.timeline import TimelinePanel
from .panels.variables import VariablesPanel
from .panels.errors import ErrorsPanel


@dataclass
class DebugToolbarConfig:
    """Configuration for debug toolbar plugin."""
    
    enabled: bool = True
    auto_show: bool = True
    intercept_redirects: bool = True
    theme: str = "dark"
    position: str = "bottom"
    three_enabled: bool = True
    three_theme: str = "dark"
    animate_transitions: bool = True
    performance_mode: str = "balanced"
    panels: List[str] = field(default_factory=lambda: [
        "request", "sql", "cache", "logging", "routing",
        "middleware", "templates", "timeline", "variables", "errors"
    ])
    sql_max_queries: int = 100
    sql_slow_threshold: int = 100
    body_truncate: int = 1000
    show_env: bool = False
    
    @classmethod
    def from_env(cls) -> "DebugToolbarConfig":
        """Load configuration from environment variables."""
        return cls(
            enabled=os.environ.get("DEBUG_TOOLBAR_ENABLED", "true").lower() == "true",
            auto_show=os.environ.get("DEBUG_TOOLBAR_AUTO_SHOW", "true").lower() == "true",
            intercept_redirects=os.environ.get("DEBUG_TOOLBAR_INTERCEPT_REDIRECTS", "true").lower() == "true",
            theme=os.environ.get("DEBUG_TOOLBAR_THEME", "dark"),
            position=os.environ.get("DEBUG_TOOLBAR_POSITION", "bottom"),
            three_enabled=os.environ.get("DEBUG_TOOLBAR_THREE_ENABLED", "true").lower() == "true",
            three_theme=os.environ.get("DEBUG_TOOLBAR_THREE_THEME", "dark"),
            animate_transitions=os.environ.get("DEBUG_TOOLBAR_ANIMATE_TRANSITIONS", "true").lower() == "true",
            performance_mode=os.environ.get("DEBUG_TOOLBAR_PERFORMANCE_MODE", "balanced"),
            sql_max_queries=int(os.environ.get("DEBUG_TOOLBAR_SQL_MAX_QUERIES", "100")),
            sql_slow_threshold=int(os.environ.get("DEBUG_TOOLBAR_SQL_THRESHOLD", "100")),
            body_truncate=int(os.environ.get("DEBUG_TOOLBAR_BODY_TRUNCATE", "1000")),
            show_env=os.environ.get("DEBUG_TOOLBAR_SHOW_ENV", "false").lower() == "true",
        )


class DebugToolbarPlugin(Plugin):
    """
    Debug toolbar plugin for Flaxon with Three.js 3D visualizations.
    
    Usage:
    
        from flaxon import Flaxon
        from flaxon_debug_toolbar import DebugToolbarPlugin
        
        app = Flaxon("my-app", debug=True)
        
        # Basic usage
        app.plugins.load_plugin(DebugToolbarPlugin())
        
        # With Three.js visualizations
        app.plugins.load_plugin(DebugToolbarPlugin(
            three_enabled=True,
            three_theme="dark",
            animate_transitions=True,
            performance_mode="balanced",
        ))
    """
    
    name = "debug_toolbar"
    version = "0.1.0"
    description = "Debug toolbar plugin for Flaxon with Three.js 3D visualizations"
    author = "Aldane Hutchinson"
    requires = []
    
    def __init__(
        self,
        enabled: bool = True,
        auto_show: bool = True,
        intercept_redirects: bool = True,
        theme: str = "dark",
        position: str = "bottom",
        three_enabled: bool = True,
        three_theme: str = "dark",
        animate_transitions: bool = True,
        performance_mode: str = "balanced",
        panels: Optional[List[str]] = None,
        sql_max_queries: int = 100,
        sql_slow_threshold: int = 100,
        body_truncate: int = 1000,
        show_env: bool = False,
        config: Optional[DebugToolbarConfig] = None,
    ):
        """
        Initialize debug toolbar plugin.
        
        Args:
            enabled: Enable/disable toolbar
            auto_show: Show toolbar automatically
            intercept_redirects: Show toolbar on redirects
            theme: "dark" or "light"
            position: "bottom" or "top"
            three_enabled: Enable Three.js visualizations
            three_theme: "dark" or "light" for 3D scenes
            animate_transitions: Animate panel transitions
            performance_mode: "performance", "balanced", "quality"
            panels: List of enabled panels
            sql_max_queries: Max SQL queries to display
            sql_slow_threshold: Slow query threshold (ms)
            body_truncate: Truncate body size
            show_env: Show environment variables
            config: DebugToolbarConfig instance
        """
        # Load config
        if config:
            self.config = config
        else:
            env_config = DebugToolbarConfig.from_env()
            self.config = DebugToolbarConfig(
                enabled=enabled if enabled is not None else env_config.enabled,
                auto_show=auto_show if auto_show is not None else env_config.auto_show,
                intercept_redirects=intercept_redirects if intercept_redirects is not None else env_config.intercept_redirects,
                theme=theme or env_config.theme,
                position=position or env_config.position,
                three_enabled=three_enabled if three_enabled is not None else env_config.three_enabled,
                three_theme=three_theme or env_config.three_theme,
                animate_transitions=animate_transitions if animate_transitions is not None else env_config.animate_transitions,
                performance_mode=performance_mode or env_config.performance_mode,
                panels=panels or env_config.panels,
                sql_max_queries=sql_max_queries or env_config.sql_max_queries,
                sql_slow_threshold=sql_slow_threshold or env_config.sql_slow_threshold,
                body_truncate=body_truncate or env_config.body_truncate,
                show_env=show_env if show_env is not None else env_config.show_env,
            )
        
        # Panel registry
        self._panels: Dict[str, Panel] = {}
        self._request_data: Dict[str, Any] = {}
        self._app = None
    
    def setup(self, app: Flaxon) -> None:
        """
        Setup the plugin with the Flaxon application.
        
        Args:
            app: Flaxon application
        """
        self._app = app
        app.state.debug_toolbar = self
        self._register_default_panels()
    
    def on_load(self) -> None:
        """Called when plugin is loaded."""
        pass
    
    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        self._request_data.clear()
    
    def on_startup(self) -> None:
        """Called on application startup."""
        pass
    
    def on_shutdown(self) -> None:
        """Called on application shutdown."""
        self._request_data.clear()
    
    def add_middleware(self, app) -> Callable:
        """
        Add debug toolbar middleware to the app.
        
        Args:
            app: ASGI application
            
        Returns:
            Wrapped application
        """
        if self.config.enabled:
            return DebugToolbarMiddleware(app, self)
        return app
    
    def _register_default_panels(self) -> None:
        """Register default panels."""
        panel_map = {
            "request": RequestPanel,
            "sql": SQLPanel,
            "cache": CachePanel,
            "logging": LoggingPanel,
            "routing": RoutingPanel,
            "middleware": MiddlewarePanel,
            "templates": TemplatesPanel,
            "timeline": TimelinePanel,
            "variables": VariablesPanel,
            "errors": ErrorsPanel,
        }
        
        for panel_id, panel_class in panel_map.items():
            if panel_id in self.config.panels:
                self.register_panel(panel_class())
    
    def register_panel(self, panel: Panel) -> None:
        """
        Register a custom panel.
        
        Args:
            panel: Panel instance
        """
        self._panels[panel.identifier] = panel
    
    async def process_request(self, request: Request) -> None:
        """
        Process a request and collect data.
        
        Args:
            request: Current request
        """
        if not self.config.enabled:
            return
        
        # Create request data container
        data = {
            "request_id": id(request),
            "start_time": time.time(),
            "request": request,
            "panels": {},
        }
        
        # Process each panel
        for panel_id, panel in self._panels.items():
            try:
                panel_data = await panel.process_request(request, data)
                data["panels"][panel_id] = panel_data
            except Exception as e:
                # Don't let panel errors break the request
                data["panels"][panel_id] = {"error": str(e)}
        
        # Store data
        self._request_data[data["request_id"]] = data
    
    async def process_response(self, request: Request, response: Response) -> None:
        """
        Process a response and collect data.
        
        Args:
            request: Current request
            response: Response
        """
        if not self.config.enabled:
            return
        
        request_id = id(request)
        data = self._request_data.get(request_id)
        if not data:
            return
        
        data["end_time"] = time.time()
        data["duration"] = data["end_time"] - data["start_time"]
        data["response"] = response
        
        # Process each panel
        for panel_id, panel in self._panels.items():
            try:
                await panel.process_response(request, response, data)
            except Exception:
                pass
    
    def get_panel_data(self, request_id: int) -> Optional[Dict[str, Any]]:
        """
        Get data for a request.
        
        Args:
            request_id: Request ID
            
        Returns:
            Request data or None
        """
        return self._request_data.get(request_id)
    
    def get_enabled_panels(self) -> List[Panel]:
        """
        Get list of enabled panels.
        
        Returns:
            List of enabled panels
        """
        return list(self._panels.values())
    
    def is_enabled(self) -> bool:
        """
        Check if toolbar is enabled.
        
        Returns:
            True if enabled
        """
        return self.config.enabled
    
    def get_three_config(self) -> Dict[str, Any]:
        """
        Get Three.js configuration.
        
        Returns:
            Three.js configuration dict
        """
        return {
            "enabled": self.config.three_enabled,
            "theme": self.config.three_theme,
            "animate_transitions": self.config.animate_transitions,
            "performance_mode": self.config.performance_mode,
        }
    
    def get_theme(self) -> str:
        """
        Get theme.
        
        Returns:
            Theme string
        """
        return self.config.theme
    
    def get_position(self) -> str:
        """
        Get position.
        
        Returns:
            Position string
        """
        return self.config.position
    
    def get_panel_by_id(self, panel_id: str) -> Optional[Panel]:
        """
        Get a panel by its ID.
        
        Args:
            panel_id: Panel identifier
            
        Returns:
            Panel instance or None
        """
        return self._panels.get(panel_id)
    
    def get_all_panel_data(self) -> Dict[str, Any]:
        """
        Get all panel data for the current request.
        
        Returns:
            Dictionary of panel data
        """
        return {
            panel_id: panel._data
            for panel_id, panel in self._panels.items()
            if hasattr(panel, "_data")
        }
    
    def clear_request_data(self) -> None:
        """Clear all stored request data."""
        self._request_data.clear()
    
    def get_config(self) -> DebugToolbarConfig:
        """
        Get plugin configuration.
        
        Returns:
            Plugin configuration
        """
        return self.config
    
    def get_panel_count(self) -> int:
        """
        Get number of registered panels.
        
        Returns:
            Panel count
        """
        return len(self._panels)
    
    def get_panel_ids(self) -> List[str]:
        """
        Get list of registered panel IDs.
        
        Returns:
            List of panel IDs
        """
        return list(self._panels.keys())