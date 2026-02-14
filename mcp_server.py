#!/usr/bin/env python3
"""
MCP Server for Gmail Send Skill

Provides Model Context Protocol (MCP) server implementation
for AI agent integration. Supports sending emails via Gmail
using App Password authentication with Markdown content support.

Usage: python mcp_server.py
Test: python mcp_server.py --test
"""

import json
import sys
import asyncio
import logging
from typing import Any, Dict, List
from datetime import datetime

# Import skill with fallback
try:
    from gmail_send_skill import GmailSendSkill
    from skill_compat import ExecutionContext
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    print("Error: Missing required modules. Please ensure gmail_send_skill.py and skill_compat.py are present.")
    sys.exit(1)

# Import version information
try:
    from version import __version__, get_version_string, get_version_info
except ImportError:
    __version__ = "1.0.0"
    get_version_string = lambda: f"Gmail Send MCP Server v{__version__}"
    get_version_info = lambda: {"version": __version__, "description": "Gmail Send MCP Server"}

class GmailSendMcpServer:
    """MCP Server for Gmail Send Skill"""
    
    def __init__(self):
        self.skill = GmailSendSkill()
        self.context = ExecutionContext()
        self.logger = logging.getLogger(__name__)
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information including version details"""
        return {
            "name": "gmail-send-mcp-server",
            "version": __version__,
            "description": f"MCP server for Gmail email sending - {get_version_string()}",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": True
            },
            "version_info": get_version_info()
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        schema = self.skill.get_openai_schema()
        return [{
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
            "inputSchema": schema["function"]["parameters"]
        }]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        if name != "gmail_send":
            return {"error": f"Unknown tool: {name}"}
        
        try:
            self.logger.info(f"Executing tool: {name} with arguments: {list(arguments.keys())}")
            result = self.skill.execute(self.context, **arguments)
            
            if result.get("success"):
                # Format successful response for MCP
                content_data = {
                    "tool_result": result,
                    "execution_time": datetime.now().isoformat(),
                    "tool_name": name
                }
                
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(content_data, ensure_ascii=False, indent=2)
                    }]
                }
            else:
                # Return error details
                error_msg = result.get("error", {}).get("message", "Unknown error")
                error_type = result.get("error", {}).get("type", "unknown")
                
                return {
                    "error": f"Tool execution failed ({error_type}): {error_msg}"
                }
                
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        resources = self.skill.get_mcp_resources()
        return [{
            "uri": resource.uri,
            "name": resource.name,
            "description": resource.description,
            "mimeType": resource.mime_type
        } for resource in resources]
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource by URI"""
        try:
            self.logger.info(f"Reading resource: {uri}")
            return self.skill.read_resource(uri)
        except Exception as e:
            self.logger.error(f"Failed to read resource {uri}: {str(e)}")
            return {
                "error": f"Failed to read resource: {str(e)}",
                "contents": [{
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": f"Error reading resource: {str(e)}"
                }]
            }
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts"""
        prompts = self.skill.get_mcp_prompts()
        return [prompt.to_dict() for prompt in prompts]
    
    def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a prompt by name"""
        try:
            self.logger.info(f"Getting prompt: {name}")
            return self.skill.get_prompt(name, arguments or {})
        except Exception as e:
            self.logger.error(f"Failed to get prompt {name}: {str(e)}")
            return {
                "error": f"Failed to get prompt: {str(e)}",
                "description": f"Prompt {name} not found",
                "messages": []
            }


class StdioTransport:
    """Standard I/O transport for MCP communication"""
    
    def __init__(self, server: GmailSendMcpServer):
        self.server = server
        self.logger = logging.getLogger(f"{__name__}.StdioTransport")
    
    async def run(self):
        """Run the stdio transport loop"""
        self.logger.info("Starting MCP server stdio transport")
        
        while True:
            try:
                # Read from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    self.logger.info("EOF received, shutting down")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    self.logger.debug(f"Received request: {request.get('method', 'unknown')}")
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                        "id": None
                    }
                    print(json.dumps(error_response, ensure_ascii=False), flush=True)
                    continue
                
                # Handle the request
                response = self.handle_request(request)
                
                # Add request ID if present
                if "id" in request:
                    response["id"] = request["id"]
                
                # Add JSON-RPC version
                response["jsonrpc"] = "2.0"
                
                # Send response
                print(json.dumps(response, ensure_ascii=False), flush=True)
                
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received, shutting down")
                break
            except Exception as e:
                self.logger.error(f"Transport error: {str(e)}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                    "id": None
                }
                print(json.dumps(error_response, ensure_ascii=False), flush=True)
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request"""
        method = request.get("method", "")
        params = request.get("params", {})
        
        self.logger.debug(f"Handling method: {method}")
        
        try:
            if method == "initialize":
                return {
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"subscribe": False, "listChanged": True},
                            "prompts": {"listChanged": True}
                        },
                        "serverInfo": self.server.get_server_info()
                    }
                }
                
            elif method == "initialized":
                return {"result": {}}
                
            elif method == "tools/list":
                tools = self.server.list_tools()
                return {"result": {"tools": tools}}
                
            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = self.server.call_tool(tool_name, arguments)
                return {"result": result}
                
            elif method == "resources/list":
                resources = self.server.list_resources()
                return {"result": {"resources": resources}}
                
            elif method == "resources/read":
                uri = params.get("uri", "")
                result = self.server.read_resource(uri)
                return {"result": result}
                
            elif method == "prompts/list":
                prompts = self.server.list_prompts()
                return {"result": {"prompts": prompts}}
                
            elif method == "prompts/get":
                name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = self.server.get_prompt(name, arguments)
                return {"result": result}
                
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error handling method {method}: {str(e)}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }


async def run_server():
    """Run the MCP server"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('gmail_send_mcp.log'), logging.StreamHandler(sys.stderr)]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Gmail Send MCP Server")
    
    try:
        server = GmailSendMcpServer()
        transport = StdioTransport(server)
        await transport.run()
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


def test_server():
    """Test the MCP server functionality"""
    print("Testing Gmail Send MCP Server...")
    
    try:
        server = GmailSendMcpServer()
        
        # Test server info
        info = server.get_server_info()
        print(f"✓ Server info: {info['name']} v{info['version']}")
        
        # Test tools list
        tools = server.list_tools()
        print(f"✓ Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description'][:50]}...")
        
        # Test resources list
        resources = server.list_resources()
        print(f"✓ Available resources: {len(resources)}")
        for resource in resources:
            print(f"  - {resource['uri']}: {resource['description'][:50]}...")
        
        # Test prompts list
        prompts = server.list_prompts()
        print(f"✓ Available prompts: {len(prompts)}")
        for prompt in prompts:
            print(f"  - {prompt['name']}: {prompt['description'][:50]}...")
        
        print("\n✓ All tests passed! Server is ready.")
        print("\nTo run the MCP server:")
        print("python mcp_server.py")
        print("\nTo integrate with Claude Desktop, see mcp_config.json")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        sys.exit(1)


async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_server()
    else:
        await run_server()


if __name__ == "__main__":
    asyncio.run(main())