from mcp.server.fastmcp import FastMCP
from config import Configuration
import llmRouterTools
from neo4jAdpater import Neo4jAdapter
from graphMutationOchestration.ochestrationTools import register_tools as register_orchestration_tools
from graphInspectionOrchestration.inspectionOchestrationTools import register_tools as register_inspection_tools

mcp = FastMCP(
    'Neo4jServer', 
    host='0.0.0.0',
    port=7674,
    json_response=True
)

neo4j_adapter = Neo4jAdapter(config=Configuration.Neo4j_Config)
llmRouterTools.register_tools(mcp, neo4j_adapter)
register_orchestration_tools(mcp, neo4j_adapter)
register_inspection_tools(mcp, neo4j_adapter)

llmRouterTools.register_prompts(mcp)

if __name__ == "__main__":
    mcp.run(transport='stdio')