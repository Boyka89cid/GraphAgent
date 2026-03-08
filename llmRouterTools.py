from neo4jAdpater import Neo4jAdapter
from mcp.server.fastmcp import FastMCP
from toolDescription import ToolPrompts, ToolsDescription
import inspect
from mcp.server.fastmcp.prompts.base import Prompt

def register_tools(mcp: FastMCP, neo4j_adapter: Neo4jAdapter):
    neo4j_tool = Neo4JLLMRouterTool(mcp, neo4j_adapter)
    available_tools = [name for name, _ in inspect.getmembers(Neo4JLLMRouterTool, predicate=inspect.isfunction) if not name.startswith("_")]

    for tool_name in available_tools:
         mcp.add_tool(
            getattr(neo4j_tool, tool_name),
            name=tool_name,
            description=getattr(ToolsDescription, tool_name, "No description available."),
        )

def register_prompts(mcp: FastMCP):
    available_tools = [
        name for name, _ in inspect.getmembers(Neo4JLLMRouterTool, predicate=inspect.isfunction)
        if not name.startswith("_")
    ]

    for tool_name in available_tools:
        prompt_text = getattr(ToolPrompts, tool_name, "No prompt available.")
        
        def _prompt(prompt_text=prompt_text):
            return prompt_text

        prompt_obj = Prompt.from_function(
            _prompt,
            name=f"{tool_name}_prompt",
            description=f"Prompt for {tool_name}",
        )

        mcp.add_prompt(prompt_obj)  # ✅ no name=

class Neo4JLLMRouterTool:

    def __init__(self, mcp: FastMCP, neo4j_adapter: Neo4jAdapter):
        self.mcp = mcp
        self.neo4j_adapter = neo4j_adapter

    def check_neo4j_connection(self) -> bool:
        """Check if the Neo4j database is reachable."""
        try:
            return self.neo4j_adapter.verify_connection()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Neo4j: {str(e)}")
    
    def show_all_databases(self) -> list:
        """Show all databases in the Neo4j instance."""
        try:
            query = "SHOW DATABASES"
            databases = self.neo4j_adapter.run_query(query)
            results = [db['name'] for db in databases if 'name' in db]
            results.remove('system')  # Remove system database from results
            #await self.mcp.get_context().session.send_log_message("critical", f"Databases: {results}")
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to fetch databases: {str(e)}")
    
