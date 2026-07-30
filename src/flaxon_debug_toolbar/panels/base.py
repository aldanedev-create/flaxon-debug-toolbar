"""Base panel class for debug toolbar."""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from flaxon.http import Request, Response


class Panel(ABC):
    """
    Base class for all debug toolbar panels.
    
    Panels collect and display data about requests and responses.
    """
    
    # Display properties
    title: str = "Panel"
    nav_title: str = "Panel"
    identifier: str = "panel"
    icon: str = "📊"
    order: int = 100
    
    # Three.js properties
    has_three_scene: bool = False
    three_scene_class: Optional[str] = None
    
    def __init__(self):
        """Initialize panel."""
        self._data: Dict[str, Any] = {}
    
    @abstractmethod
    async def process_request(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request data.
        
        Args:
            request: Current request
            data: Request data container
            
        Returns:
            Panel data
        """
        pass
    
    @abstractmethod
    async def process_response(self, request: Request, response: Response, data: Dict[str, Any]) -> None:
        """
        Process response data.
        
        Args:
            request: Current request
            response: Response
            data: Request data container
        """
        pass
    
    @abstractmethod
    async def render(self, context: Dict[str, Any]) -> str:
        """
        Render panel HTML.
        
        Args:
            context: Template context
            
        Returns:
            Rendered HTML
        """
        pass
    
    async def get_context(self) -> Dict[str, Any]:
        """
        Get panel context data.
        
        Returns:
            Context dictionary
        """
        return self._data
    
    async def get_three_data(self) -> Dict[str, Any]:
        """
        Get data for Three.js visualization.
        
        Returns:
            Three.js data
        """
        return {}
    
    def get_order(self) -> int:
        """Get panel order."""
        return self.order