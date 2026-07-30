"""Panels for Flaxon debug toolbar."""

from .base import Panel
from .request import RequestPanel
from .sql import SQLPanel
from .cache import CachePanel
from .logging import LoggingPanel
from .routing import RoutingPanel
from .middleware import MiddlewarePanel
from .templates import TemplatesPanel
from .timeline import TimelinePanel
from .variables import VariablesPanel
from .errors import ErrorsPanel

__all__ = [
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