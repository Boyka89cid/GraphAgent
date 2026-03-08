from mcp.server.fastmcp import FastMCP
from typing import Any, Dict
import inspect
from graphInspectionOrchestration.inspectionSessionDataClasses import (
    SessionStateForCountNodesByLabel, 
    SessionStateForCountRelationshipsByType, 
    SessionStateNodeCountGraph
    )
from graphInspectionOrchestration.inspectionSessionSteps import (
    CountNodesByLabelSteps,
    CountRelationshipsByTypeSteps,
    GraphNodeCountSteps
    )
from graphInspectionOrchestration.inspectionToolDescriptions import InspectionToolPrompts
from neo4jAdpater import Neo4jAdapter
from graphInspectionOrchestration.inspectionHelperFxns import InspectionHelperFxns
from graphMutationOchestration.validationHelperFxns import ValidationHelperFxns

GRAPHNODECOUNTSESSION: Dict[str, SessionStateNodeCountGraph] = {}
COUNTNODESBYLABELSESSIONS: Dict[str, SessionStateForCountNodesByLabel] = {}
COUNTRELATIONSHIPSBYTYPESESSIONS: Dict[str, SessionStateForCountRelationshipsByType] = {}

def register_tools(mcp: FastMCP, neo4j_adapter: Neo4jAdapter):
    inspection_helper_fxns = InspectionHelperFxns(neo4j_adapter, ValidationHelperFxns(neo4j_adapter=neo4j_adapter))
    neo4j_tool = GraphInspectionOrchestrationTools(neo4j_adapter, inspection_helper_fxns)
    available_tools = [name for name, _ in inspect.getmembers(GraphInspectionOrchestrationTools, predicate=inspect.isfunction) if not name.startswith("_")]

    for tool_name in available_tools:
         mcp.add_tool(
            getattr(neo4j_tool, tool_name),
            name=tool_name,
            description=getattr(InspectionToolPrompts, tool_name, "No description available."),
        )

class GraphInspectionOrchestrationTools:

    def __init__(self, neo4j_adapter: Neo4jAdapter, inspection_helper_fxns: InspectionHelperFxns):
        self.neo4j_adapter = neo4j_adapter
        self.inspection_helper_fxns = inspection_helper_fxns

    def graph_nodes_count(self, session_state: SessionStateNodeCountGraph) -> Dict[str, Any]:

        def decide_step(s: SessionStateNodeCountGraph) -> str:
            has_graph_name = bool((s.graph_name or "").strip())

            if not has_graph_name:
                return GraphNodeCountSteps.ASK_GRAPH_NAME.value
            return GraphNodeCountSteps.GET_GRAPH_NODE_COUNT.value

        session = GRAPHNODECOUNTSESSION.setdefault(session_state.session_id, session_state)

        if session_state.graph_name is not None:
            session.graph_name = session_state.graph_name

        session.step = decide_step(session)

        if session.step == GraphNodeCountSteps.ASK_GRAPH_NAME.value:
            try:
                available_graphs = self.inspection_helper_fxns.get_available_graphs()
                return {
                    "status": "ask_graph_name",
                    "message": "Please provide the graph name.",
                    "available_graphs": available_graphs
                }
            except Exception as e:
                return {
                    "status": "ask_graph_name",
                    "message": "Please provide the graph name.",
                    "available_graphs": [],
                    "warning": str(e)
                }

        elif session.step == GraphNodeCountSteps.GET_GRAPH_NODE_COUNT.value:
            try:
                result = self.inspection_helper_fxns.get_graph_counts(session.graph_name)

                session.node_count = result.get("node_count", 0)
                session.relationship_count = result.get("relationship_count", 0)

                response = {
                    "status": "success",
                    "message": f"Graph '{session.graph_name}' has {session.node_count} nodes and {session.relationship_count} relationships/edges.",
                    "data": {
                        "graph_name": session.graph_name,
                        "node_count": session.node_count,
                        "relationship_count": session.relationship_count
                    }
                }

                GRAPHNODECOUNTSESSION.pop(session.session_id, None)
                return response

            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }

        else:
            GRAPHNODECOUNTSESSION.pop(session.session_id, None)
            return {
                "status": "completed",
                "message": "Graph node count process completed."
            }

    def count_nodes_by_label(self, session_state: SessionStateForCountNodesByLabel) -> Dict[str, Any]:

        def decide_step(s: SessionStateForCountNodesByLabel) -> str:
            has_graph_name = bool((s.graph_name or "").strip())
            has_node_label = bool((s.node_label or "").strip())

            if not has_graph_name:
                return CountNodesByLabelSteps.ASK_GRAPH_NAME.value
            if has_graph_name and not has_node_label:
                return CountNodesByLabelSteps.ASK_NODE_LABEL.value
            return CountNodesByLabelSteps.COUNT_NODES_BY_LABEL.value

        session = COUNTNODESBYLABELSESSIONS.setdefault(session_state.session_id, session_state)

        if session_state.graph_name is not None:
            session.graph_name = session_state.graph_name
        if session_state.node_label is not None:
            session.node_label = session_state.node_label

        session.step = decide_step(session)

        if session.step == CountNodesByLabelSteps.ASK_GRAPH_NAME.value:
            try:
                available_graphs = self.inspection_helper_fxns.get_available_graphs()
                return {
                    "status": "ask_graph_name",
                    "message": "Please provide the graph name.",
                    "available_graphs": available_graphs
                }
            except Exception as e:
                return {
                    "status": "ask_graph_name",
                    "message": "Please provide the graph name.",
                    "available_graphs": [],
                    "warning": str(e)
                }

        elif session.step == CountNodesByLabelSteps.ASK_NODE_LABEL.value:
            try:
                available_labels = self.inspection_helper_fxns.get_available_labels(session.graph_name)
                return {
                    "status": "ask_node_label",
                    "message": "Please provide the node label.",
                    "available_labels": available_labels
                }
            except Exception as e:
                return {
                    "status": "ask_node_label",
                    "message": "Please provide the node label.",
                    "available_labels": [],
                    "warning": str(e)
                }

        elif session.step == CountNodesByLabelSteps.COUNT_NODES_BY_LABEL.value:
            try:
                result = self.inspection_helper_fxns.count_nodes_by_label(
                    graph_name=session.graph_name,
                    node_label=session.node_label
                )

                COUNTNODESBYLABELSESSIONS.pop(session.session_id, None)
                return {
                    "status": "node_count_by_label_fetched",
                    "message": f"Graph '{session.graph_name}' has {result.get('node_count', 0)} nodes with label '{session.node_label}'.",
                    "data": {
                        "graph_name": session.graph_name,
                        "node_label": session.node_label,
                        "node_count": result.get("node_count", 0)
                    }
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        else:
            COUNTNODESBYLABELSESSIONS.pop(session.session_id, None)
            return {
                "status": "completed",
                "message": "Count nodes by label process completed."
            }
    
    def count_relationships_by_type(self, session_state: SessionStateForCountRelationshipsByType) -> Dict[str, Any]:

        def decide_step(s: SessionStateForCountRelationshipsByType) -> str:
            has_graph_name = bool((s.graph_name or "").strip())
            has_relationship_type = bool((s.relationship_type or "").strip())

            if not has_graph_name:
                return CountRelationshipsByTypeSteps.ASK_GRAPH_NAME.value
            if has_graph_name and not has_relationship_type:
                return CountRelationshipsByTypeSteps.ASK_RELATIONSHIP_TYPE.value
            return CountRelationshipsByTypeSteps.COUNT_RELATIONSHIPS_BY_TYPE.value

        session = COUNTRELATIONSHIPSBYTYPESESSIONS.setdefault(session_state.session_id, session_state)

        if session_state.graph_name is not None:
            session.graph_name = session_state.graph_name
        if session_state.relationship_type is not None:
            session.relationship_type = session_state.relationship_type

        session.step = decide_step(session)

        if session.step == CountRelationshipsByTypeSteps.ASK_GRAPH_NAME.value:
            try:
                available_graphs = self.inspection_helper_fxns.get_available_graphs()
                return {
                    "status": "ask_graph_name",
                    "message": "Please provide the graph name.",
                    "available_graphs": available_graphs
                }
            except Exception as e:
                return {
                    "status": "ask_graph_name",
                    "message": "Please provide the graph name.",
                    "available_graphs": [],
                    "warning": str(e)
                }

        elif session.step == CountRelationshipsByTypeSteps.ASK_RELATIONSHIP_TYPE.value:
            try:
                available_relationship_types = self.inspection_helper_fxns.get_available_relationship_types(session.graph_name)
                return {
                    "status": "ask_relationship_type",
                    "message": "Please provide the relationship type.",
                    "available_relationship_types": available_relationship_types
                }
            except Exception as e:
                return {
                    "status": "ask_relationship_type",
                    "message": "Please provide the relationship type.",
                    "available_relationship_types": [],
                    "warning": str(e)
                }

        elif session.step == CountRelationshipsByTypeSteps.COUNT_RELATIONSHIPS_BY_TYPE.value:
            try:
                result = self.inspection_helper_fxns.count_relationships_by_type(
                    graph_name=session.graph_name,
                    relationship_type=session.relationship_type
                )

                COUNTRELATIONSHIPSBYTYPESESSIONS.pop(session.session_id, None)
                return {
                    "status": "relationship_count_by_type_fetched",
                    "message": f"Graph '{session.graph_name}' has {result.get('relationship_count', 0)} relationships of type '{session.relationship_type}'.",
                    "data": {
                        "graph_name": session.graph_name,
                        "relationship_type": session.relationship_type,
                        "relationship_count": result.get("relationship_count", 0)
                    }
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        else:
            COUNTRELATIONSHIPSBYTYPESESSIONS.pop(session.session_id, None)
            return {
                "status": "completed",
                "message": "Count relationships by type process completed."
            }
        