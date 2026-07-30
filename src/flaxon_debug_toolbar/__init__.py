"""Flaxon Debug Toolbar - Debug toolbar plugin for Flaxon with Three.js 3D visualizations."""

from .plugin import DebugToolbarPlugin, DebugToolbarConfig
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

__all__ = [
    "DebugToolbarPlugin",
    "DebugToolbarConfig",
    "Panel",
    "RequestPanel",
    "SQLPanel",
    "CachePanel",
    "LoggingPanel",
    "RoutingPanel",
    "MiddlewarePanel",
    "TemplatesPanel",
    "TimelinePanel",
    "VariablesPanel",
    "ErrorsPanel",
]

__version__ = "0.1.0"