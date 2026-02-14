from mcp.server.fastmcp import FastMCP
from neo4jAdpater import Neo4jAdapter
from toolDescription import ToolPrompts, ToolsDescription
from dataclasses import dataclass
from typing import Dict

@dataclass
class SessionStateNodeCountGraph:
    session_id: str
    graph_name: str = ''
    node_count: int = 0
    relationship_count: int = 0

GRAPHNODECOUNTSESSION: Dict[str, SessionStateNodeCountGraph] = {}

class OchestrationTools:
    def __init__(self, mcp: FastMCP, neo4j_adapter: Neo4jAdapter):
        self.mcp = mcp
        self.neo4j_adapter = neo4j_adapter
    
    def update_session_graph_node_count(self, session_state: SessionStateNodeCountGraph):

        session = GRAPHNODECOUNTSESSION.setdefault(session_state.session_id, session_state)

        if session.graph_name is not None:
            session.graph_name = session_state.graph_name
        
        """Update the session state with the node count for a specific graph."""
        if session.graph_name is None:
            print(f"Graph name is not set for session {session.session_id}. Cannot update node count.")
            return {
                'status': 'ask_graph_name',
                'message': 'Please provide the graph name to update node count.'
            }
        else:
            try:
                query = f"USE {session.graph_name} RETURN count(*) AS node_count, count(r) AS relationship_count"
                result = self.neo4j_adapter.run_query(query)
                if result:
                    node_count = result[0].get('node_count', 0)
                    relationship_count = result[0].get('relationship_count', 0)
                    GRAPHNODECOUNTSESSION[session.session_id] = SessionStateNodeCountGraph(
                        session_id=session.session_id,
                        graph_name=session.graph_name,
                        node_count=node_count,
                        relationship_count=relationship_count
                    )
                return {
                    'status': 'success',
                    'message': f"Graph '{session.graph_name}' has {node_count} nodes and {relationship_count} relationships."
                }
            except Exception as e:
                print(f"Error updating session graph node count: {e}")


