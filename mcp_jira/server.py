"""MCP JIRA Server main orchestrator."""
from typing import Any
import inspect
from functools import wraps

from .credentials import CredentialsManager
from .tools import ALL_TOOLS, MCPTool

try:
    from fastmcp import FastMCP, Context
except ImportError:
    raise ImportError("fastmcp is required. Install with: pip install fastmcp")


class MCPJiraServer:
    """Main MCP JIRA Server orchestrator with plugin-based tool architecture."""
    
    def __init__(self):
        """Initialize the server and register all tools."""
        self.credentials_manager = CredentialsManager()
        self.mcp = FastMCP("mcp-jira")
        
        self.tools: list[MCPTool] = []
        self._initialize_tools()
        self._register_tools()

    def _initialize_tools(self):
        """Initialize all tool instances."""
        for tool_class in ALL_TOOLS:
            tool_instance = tool_class(
                credentials_manager=self.credentials_manager
            )
            self.tools.append(tool_instance)
            print(f"[init] Initialized tool: {tool_instance.name}")

    def _register_tools(self):
        """Register all tools with FastMCP."""
        for tool in self.tools:
            self._register_single_tool(tool)
    
    def _register_single_tool(self, tool: MCPTool):
        """
        Register a single tool with FastMCP.
        
        Args:
            tool: The tool instance to register
        """
        execute_method = tool.execute
        sig = inspect.signature(execute_method)
        
        params = []
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            params.append(param)
        
        new_sig = sig.replace(parameters=params)
        
        @wraps(execute_method)
        async def wrapper(*args, _tool=tool, **kwargs):
            return await _tool.execute(*args, **kwargs)
        
        wrapper.__signature__ = new_sig
        wrapper.__name__ = tool.name
        wrapper.__doc__ = tool.description
        
        self.mcp.tool()(wrapper)
        print(f"[register] Registered MCP tool: {tool.name}")

    def add_custom_tool(self, tool: MCPTool):
        """
        Add a custom tool dynamically.
        
        Args:
            tool: Custom tool instance that inherits from MCPTool
        """
        self.tools.append(tool)
        self._register_single_tool(tool)
        print(f"[custom] Added custom tool: {tool.name}")

    def run(self, port: int):
        """
        Start the MCP server.
        
        Args:
            port: Port number to bind the server
        """
        print(f"\n{'='*60}")
        print(f"MCP JIRA Server")
        print(f"{'='*60}")
        print(f"Port: {port}")
        print(f"Registered tools: {len(self.tools)}")
        for tool in self.tools:
            print(f"   - {tool.name}")
        print(f"{'='*60}\n")
        
        self.mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
