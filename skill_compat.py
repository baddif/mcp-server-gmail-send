"""
Skill Compatibility Layer

Provides compatibility between framework-integrated skills and standalone execution.
This allows skills to work both within the main framework and as independent MCP servers.
"""

from typing import Any, Dict, List, Optional, Protocol
from abc import ABC, abstractmethod
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionContext:
    """
    Execution context for storing and retrieving shared data between skills
    
    This provides a simple key-value store that persists during skill execution
    and allows skills to share data with each other.
    """
    
    def __init__(self):
        self._data = {}
        self.logger = logging.getLogger(f"{__name__}.ExecutionContext")
    
    def set(self, key: str, value: Any) -> None:
        """Store a value in the context"""
        self._data[key] = value
        self.logger.debug(f"Context set: {key} = {type(value).__name__}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the context"""
        value = self._data.get(key, default)
        self.logger.debug(f"Context get: {key} = {type(value).__name__}")
        return value
    
    def has(self, key: str) -> bool:
        """Check if a key exists in the context"""
        return key in self._data
    
    def remove(self, key: str) -> Any:
        """Remove and return a value from the context"""
        return self._data.pop(key, None)
    
    def clear(self) -> None:
        """Clear all data from the context"""
        self._data.clear()
        self.logger.debug("Context cleared")
    
    def keys(self) -> List[str]:
        """Get all keys in the context"""
        return list(self._data.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Return a copy of all context data"""
        return self._data.copy()


class McpResource:
    """
    Model Context Protocol Resource definition
    
    Represents a readable resource that can be accessed via URI
    """
    
    def __init__(self, uri: str, name: str, description: str, 
                 mime_type: str = "text/plain", annotations: Optional[Dict[str, Any]] = None):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self.annotations = annotations or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP protocol"""
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type,
            **self.annotations
        }


class McpPrompt:
    """
    Model Context Protocol Prompt definition
    
    Represents a structured prompt template with optional arguments
    """
    
    def __init__(self, name: str, description: str, 
                 arguments: Optional[List[Dict[str, Any]]] = None):
        self.name = name
        self.description = description
        self.arguments = arguments or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP protocol"""
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments
        }


class McpTool:
    """
    Model Context Protocol Tool definition
    
    Represents an executable tool/function
    """
    
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
    
    @classmethod
    def from_openai_schema(cls, openai_schema: Dict[str, Any]) -> 'McpTool':
        """Convert OpenAI Function Calling schema to MCP Tool"""
        function_def = openai_schema.get("function", {})
        return cls(
            name=function_def.get("name", ""),
            description=function_def.get("description", ""),
            input_schema=function_def.get("parameters", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP protocol"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


class Skill(Protocol):
    """
    Base Skill Protocol
    
    All skills must implement the execute method to be compatible
    with the framework.
    """
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """Execute the skill with given parameters"""
        ...


class McpCompatibleSkill(ABC):
    """
    Base class for MCP-compatible skills
    
    Provides the foundation for skills that support both OpenAI Function Calling
    and Model Context Protocol standards.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def get_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        pass
    
    @abstractmethod
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """Execute the skill with given parameters"""
        pass
    
    def get_mcp_tool(self) -> McpTool:
        """Convert to MCP Tool format"""
        return McpTool.from_openai_schema(self.get_openai_schema())
    
    def get_mcp_resources(self) -> List[McpResource]:
        """Define MCP Resources for this skill"""
        return []
    
    def get_mcp_prompts(self) -> List[McpPrompt]:
        """Define MCP Prompts for this skill"""
        return []
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read MCP resource by URI
        
        Override this method to provide custom resource reading logic.
        """
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": f"Resource {uri} not found in {self.__class__.__name__}"
                }
            ]
        }
    
    def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get MCP prompt by name
        
        Override this method to provide custom prompt generation logic.
        """
        return {
            "description": f"Prompt {name} not found in {self.__class__.__name__}",
            "messages": []
        }
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate parameters against the schema
        
        Returns validation result with success status and error details
        """
        try:
            schema = self.get_openai_schema()
            parameters = schema.get("function", {}).get("parameters", {})
            required = parameters.get("required", [])
            properties = parameters.get("properties", {})
            
            # Check required parameters
            for param in required:
                if param not in kwargs or kwargs[param] is None:
                    return {
                        "success": False,
                        "error": f"Required parameter '{param}' is missing"
                    }
            
            # Validate parameter types (basic validation)
            for param, value in kwargs.items():
                if param in properties:
                    expected_type = properties[param].get("type")
                    if expected_type == "string" and not isinstance(value, str):
                        return {
                            "success": False,
                            "error": f"Parameter '{param}' must be a string"
                        }
                    elif expected_type == "integer" and not isinstance(value, int):
                        return {
                            "success": False,
                            "error": f"Parameter '{param}' must be an integer"
                        }
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        return {
                            "success": False,
                            "error": f"Parameter '{param}' must be a boolean"
                        }
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Parameter validation failed: {str(e)}"
            }
    
    def get_skill_info(self) -> Dict[str, Any]:
        """Get general information about this skill"""
        schema = self.get_openai_schema()
        function_def = schema.get("function", {})
        
        return {
            "name": function_def.get("name", "unknown"),
            "description": function_def.get("description", ""),
            "class": self.__class__.__name__,
            "mcp_resources": len(self.get_mcp_resources()),
            "mcp_prompts": len(self.get_mcp_prompts()),
            "supports_mcp": True,
            "supports_openai": True
        }


# Utility functions for skill management

def create_error_response(function_name: str, error_message: str, 
                         error_type: str = "execution_error") -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        "success": False,
        "function_name": function_name,
        "error": {
            "message": error_message,
            "type": error_type
        }
    }


def create_success_response(function_name: str, data: Any = None, 
                           result: Any = None, **metadata) -> Dict[str, Any]:
    """Create a standardized success response"""
    response = {
        "success": True,
        "function_name": function_name
    }
    
    if data is not None:
        response["data"] = data
    
    if result is not None:
        response["result"] = result
    
    if metadata:
        response["metadata"] = metadata
    
    return response


def validate_email_address(email: str) -> bool:
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """JSON dumps with safe defaults"""
    return json.dumps(obj, ensure_ascii=False, default=str, **kwargs)


# Export all public classes and functions
__all__ = [
    'ExecutionContext',
    'McpResource',
    'McpPrompt', 
    'McpTool',
    'Skill',
    'McpCompatibleSkill',
    'create_error_response',
    'create_success_response',
    'validate_email_address',
    'safe_json_dumps'
]