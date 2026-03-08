from mcp.server.fastmcp import FastMCP
from graphMutationOchestration.graphHelperFxns import GraphHelperFxns
from graphMutationOchestration.sessionDataClasses import (
    SessionStateForCreateNode,
    SessionStateForCreateRelationship,
    SessionStateForDeleteNode,
    SessionStateForDeleteRelationship, 
    SessionStateForUpdateNode
)
from graphMutationOchestration.sessionSteps import (
    CreateNodeSteps,
    CreateRelationshipSteps,
    DeleteNodeSteps, 
    DeleteRelationshipSteps,
    UpdateNodeSteps
)

from graphMutationOchestration.validationHelperFxns import ValidationHelperFxns
from neo4jAdpater import Neo4jAdapter
from graphMutationOchestration.toolDescriptions import OrchestrationToolPrompts
from typing import Any, Dict
import inspect

CREATENODESESSIONS: Dict[str, SessionStateForCreateNode] = {}
UPDATENODESESSIONS: Dict[str, SessionStateForUpdateNode] = {}
CREATERELATIONSHIPSESSIONS: Dict[str, SessionStateForCreateRelationship] = {}
DELETENODESESSIONS: Dict[str, SessionStateForDeleteNode] = {}
DELETERELATIONSHIPSESSIONS: Dict[str, SessionStateForDeleteRelationship] = {}

def register_tools(mcp: FastMCP, neo4j_adapter: Neo4jAdapter):
    graph_helper_fxns = GraphHelperFxns(neo4j_adapter, ValidationHelperFxns(neo4j_adapter=neo4j_adapter))
    neo4j_tool = GraphMutationOchestrationTools(mcp, neo4j_adapter, graph_helper_fxns)
    available_tools = [name for name, _ in inspect.getmembers(GraphMutationOchestrationTools, predicate=inspect.isfunction) if not name.startswith("_")]

    for tool_name in available_tools:
         mcp.add_tool(
            getattr(neo4j_tool, tool_name),
            name=tool_name,
            description=getattr(OrchestrationToolPrompts, tool_name, "No description available."),
        )

class GraphMutationOchestrationTools:

    def __init__(self, mcp: FastMCP, neo4j_adapter: Neo4jAdapter, graph_helper_fxns: GraphHelperFxns):
        self.mcp = mcp
        self.neo4j_adapter = neo4j_adapter
        self.graph_helper_fxns = graph_helper_fxns
    
    def create_node(self, session_state: SessionStateForCreateNode) -> Dict[str, Any]:

        def decide_step(s: SessionStateForCreateNode) -> str:
            has_graph_name = bool((s.graph_name or "").strip())
            has_labels = bool(s.labels)
            has_properties = s.properties is not None
            has_confirmation = s.user_confirmation is not None

            if not has_graph_name:
                return CreateNodeSteps.ASK_GRAPH_NAME.value
            if has_graph_name and not has_labels:
                return CreateNodeSteps.ASK_LABELS.value
            if has_graph_name and has_labels and not has_properties:
                return CreateNodeSteps.ASK_PROPERTIES.value
            if has_graph_name and has_labels and has_properties and not has_confirmation:
                return CreateNodeSteps.USER_CONFIRMATION.value
            return CreateNodeSteps.CREATE_NODE.value

        session = CREATENODESESSIONS.setdefault(session_state.session_id, session_state)

        if session_state.graph_name is not None:
            session.graph_name = session_state.graph_name
        if session_state.labels is not None:
            session.labels = session_state.labels
        if session_state.properties is not None:
            session.properties = session_state.properties
        if session_state.user_confirmation is not None:
            session.user_confirmation = session_state.user_confirmation

        session.step = decide_step(session)

        if session.step == CreateNodeSteps.ASK_GRAPH_NAME.value:
            try:
                available_graphs = self.graph_helper_fxns.get_available_graphs()
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

        elif session.step == CreateNodeSteps.ASK_LABELS.value:
            try:
                available_labels = self.graph_helper_fxns.get_available_labels(session.graph_name)
                return {
                    "status": "ask_labels",
                    "message": "Please provide one or more labels for the node.",
                    "available_labels": available_labels
                }
            except Exception as e:
                return {
                    "status": "ask_labels",
                    "message": "Please provide one or more labels for the node.",
                    "available_labels": [],
                    "warning": str(e)
                }

        elif session.step == CreateNodeSteps.ASK_PROPERTIES.value:
            try:
                available_properties = self.graph_helper_fxns.get_property_keys_for_labels(
                    graph_name=session.graph_name,
                    labels=session.labels
                )
                return {
                    "status": "ask_properties",
                    "message": "Please provide the properties for the node.",
                    "available_properties": available_properties
                }
            except Exception as e:
                return {
                    "status": "ask_properties",
                    "message": "Please provide the properties for the node.",
                    "available_properties": [],
                    "warning": str(e)
                }

        elif session.step == CreateNodeSteps.USER_CONFIRMATION.value:
            return {
                "status": "node_summary",
                "message": f"Create node in graph '{session.graph_name}' with labels {session.labels} and properties {session.properties}?"
            }

        elif session.step == CreateNodeSteps.CREATE_NODE.value:
            if not session.user_confirmation:
                CREATENODESESSIONS.pop(session.session_id, None)
                return {
                    "status": "cancelled",
                    "message": "Node creation cancelled by the user."
                }

            try:
                result = self.graph_helper_fxns.create_node(
                    session.graph_name,
                    session.labels,
                    session.properties
                )
                CREATENODESESSIONS.pop(session.session_id, None)
                return {
                    "status": "node_created",
                    "message": "Node created successfully.",
                    "data": result if result else {}
                }

            except Exception as e:
                session.properties = None
                session.step = CreateNodeSteps.ASK_PROPERTIES.value
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        else:
            CREATENODESESSIONS.pop(session.session_id, None)
            return {
                "status": "completed",
                "message": "Create node process completed."
            }
    
    def delete_node(self, session_state: SessionStateForDeleteNode) -> Dict[str, Any]:

        def decide_step(s: SessionStateForDeleteNode) -> str:
            has_graph_name = bool((s.graph_name or "").strip())
            has_known_property_key = bool((s.known_property_key or "").strip())
            has_known_property_value = s.known_property_value is not None
            has_resolved_node_id = bool((s.resolved_node_id or "").strip())
            has_confirmation = s.user_confirmation is not None

            if not has_graph_name:
                return DeleteNodeSteps.ASK_GRAPH_NAME.value
            if has_graph_name and not has_known_property_key:
                return DeleteNodeSteps.ASK_KNOWN_PROPERTY_KEY.value
            if has_graph_name and has_known_property_key and not has_known_property_value:
                return DeleteNodeSteps.ASK_KNOWN_PROPERTY_VALUE.value
            if has_graph_name and has_known_property_key and has_known_property_value and not has_resolved_node_id:
                return DeleteNodeSteps.RESOLVE_NODE.value
            if has_resolved_node_id and not has_confirmation:
                return DeleteNodeSteps.USER_CONFIRMATION.value
            return DeleteNodeSteps.DELETE_NODE.value

        session = DELETENODESESSIONS.setdefault(session_state.session_id, session_state)

        if session_state.graph_name is not None:
            session.graph_name = session_state.graph_name
        if session_state.known_property_key is not None:
            session.known_property_key = session_state.known_property_key
        if session_state.known_property_value is not None:
            session.known_property_value = session_state.known_property_value
        if session_state.resolved_node_id is not None:
            session.resolved_node_id = session_state.resolved_node_id
        if session_state.resolved_node_preview is not None:
            session.resolved_node_preview = session_state.resolved_node_preview
        if session_state.user_confirmation is not None:
            session.user_confirmation = session_state.user_confirmation

        session.step = decide_step(session)

        if session.step == DeleteNodeSteps.ASK_GRAPH_NAME.value:
            try:
                available_graphs = self.graph_helper_fxns.get_available_graphs()
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

        elif session.step == DeleteNodeSteps.ASK_KNOWN_PROPERTY_KEY.value:
            try:
                available_property_keys = self.graph_helper_fxns.get_all_node_property_keys(session.graph_name)
                return {
                    "status": "ask_known_property_key",
                    "message": "These are the available node property keys in the graph. Please tell me which property key you know for the node you want to delete.",
                    "available_property_keys": available_property_keys
                }
            except Exception as e:
                return {
                    "status": "ask_known_property_key",
                    "message": "Please provide the property key you know for the node you want to delete.",
                    "available_property_keys": [],
                    "warning": str(e)
                }

        elif session.step == DeleteNodeSteps.ASK_KNOWN_PROPERTY_VALUE.value:
            return {
                "status": "ask_known_property_value",
                "message": f"Please provide the value for property key '{session.known_property_key}'."
            }

        elif session.step == DeleteNodeSteps.RESOLVE_NODE.value:
            try:
                matched_nodes = self.graph_helper_fxns.find_nodes_by_property(
                    graph_name=session.graph_name,
                    property_key=session.known_property_key,
                    property_value=session.known_property_value
                )

                if not matched_nodes:
                    bad_value = session.known_property_value
                    session.known_property_value = None
                    return {
                        "status": "no_matching_node",
                        "message": f"No node found where {session.known_property_key} = {bad_value}. Please provide another value.",
                        "matched_nodes": []
                    }

                if len(matched_nodes) > 1:
                    bad_value = session.known_property_value
                    session.known_property_value = None
                    return {
                        "status": "multiple_matching_nodes",
                        "message": f"Multiple nodes matched where {session.known_property_key} = {bad_value}. Please provide a more specific property key or a more specific value.",
                        "matched_nodes": matched_nodes
                    }

                resolved_node = matched_nodes[0]
                session.resolved_node_id = resolved_node["node_id"]
                session.resolved_node_preview = resolved_node

                return {
                    "status": "node_resolved",
                    "message": "Matching node found. Please confirm whether you want to delete it.",
                    "resolved_node": resolved_node
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        elif session.step == DeleteNodeSteps.USER_CONFIRMATION.value:
            try:
                node_preview = self.graph_helper_fxns.preview_node_for_delete(
                    graph_name=session.graph_name,
                    node_id=session.resolved_node_id
                )
                return {
                    "status": "delete_node_summary",
                    "message": f"Delete this node from graph '{session.graph_name}'? This will detach delete the node and all its relationships.",
                    "resolved_node": node_preview if node_preview else {}
                }
            except Exception as e:
                return {
                    "status": "delete_node_summary",
                    "message": f"Delete this node from graph '{session.graph_name}'? This will detach delete the node and all its relationships.",
                    "resolved_node": {},
                    "warning": str(e)
                }

        elif session.step == DeleteNodeSteps.DELETE_NODE.value:
            if not session.user_confirmation:
                DELETENODESESSIONS.pop(session.session_id, None)
                return {
                    "status": "cancelled",
                    "message": "Node deletion cancelled by the user."
                }

            try:
                result = self.graph_helper_fxns.delete_node_with_confirmation(
                    graph_name=session.graph_name,
                    node_id=session.resolved_node_id
                )

                if not result:
                    session.resolved_node_id = None
                    session.resolved_node_preview = None
                    session.step = DeleteNodeSteps.ASK_KNOWN_PROPERTY_VALUE.value
                    return {
                        "status": "error, call the tool again with correct details",
                        "message": "The resolved node could not be deleted."
                    }

                DELETENODESESSIONS.pop(session.session_id, None)
                return {
                    "status": "node_deleted",
                    "message": "Node deleted successfully.",
                    "data": result
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        else:
            DELETENODESESSIONS.pop(session.session_id, None)
            return {
                "status": "completed",
                "message": "Delete node process completed."
            }

    def update_node(self, session_state: SessionStateForUpdateNode) -> Dict[str, Any]:

        def decide_step(s: SessionStateForUpdateNode) -> str:
            has_graph_name = bool((s.graph_name or "").strip())
            has_known_property_key = bool((s.known_property_key or "").strip())
            has_known_property_value = s.known_property_value is not None
            has_resolved_node_id = bool((s.resolved_node_id or "").strip())
            has_properties_to_update = s.properties_to_update is not None
            has_confirmation = s.user_confirmation is not None

            if not has_graph_name:
                return UpdateNodeSteps.ASK_GRAPH_NAME.value
            if has_graph_name and not has_known_property_key:
                return UpdateNodeSteps.ASK_KNOWN_PROPERTY_KEY.value
            if has_graph_name and has_known_property_key and not has_known_property_value:
                return UpdateNodeSteps.ASK_KNOWN_PROPERTY_VALUE.value
            if has_graph_name and has_known_property_key and has_known_property_value and not has_resolved_node_id:
                return UpdateNodeSteps.RESOLVE_NODE.value
            if has_resolved_node_id and not has_properties_to_update:
                return UpdateNodeSteps.ASK_PROPERTIES_TO_UPDATE.value
            if has_resolved_node_id and has_properties_to_update and not has_confirmation:
                return UpdateNodeSteps.USER_CONFIRMATION.value
            return UpdateNodeSteps.UPDATE_NODE.value

        session = UPDATENODESESSIONS.setdefault(session_state.session_id, session_state)

        if session_state.graph_name is not None:
            session.graph_name = session_state.graph_name
        if session_state.known_property_key is not None:
            session.known_property_key = session_state.known_property_key
        if session_state.known_property_value is not None:
            session.known_property_value = session_state.known_property_value
        if session_state.resolved_node_id is not None:
            session.resolved_node_id = session_state.resolved_node_id
        if session_state.resolved_node_preview is not None:
            session.resolved_node_preview = session_state.resolved_node_preview
        if session_state.properties_to_update is not None:
            session.properties_to_update = session_state.properties_to_update
        if session_state.user_confirmation is not None:
            session.user_confirmation = session_state.user_confirmation

        session.step = decide_step(session)

        if session.step == UpdateNodeSteps.ASK_GRAPH_NAME.value:
            try:
                available_graphs = self.graph_helper_fxns.get_available_graphs()
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

        elif session.step == UpdateNodeSteps.ASK_KNOWN_PROPERTY_KEY.value:
            try:
                available_property_keys = self.graph_helper_fxns.get_all_node_property_keys(session.graph_name)
                return {
                    "status": "ask_known_property_key",
                    "message": "These are the available node property keys in the graph. Please tell me which property key you know for the node you want to update.",
                    "available_property_keys": available_property_keys
                }
            except Exception as e:
                return {
                    "status": "ask_known_property_key",
                    "message": "Please provide the property key you know for the node you want to update.",
                    "available_property_keys": [],
                    "warning": str(e)
                }

        elif session.step == UpdateNodeSteps.ASK_KNOWN_PROPERTY_VALUE.value:
            return {
                "status": "ask_known_property_value",
                "message": f"Please provide the value for property key '{session.known_property_key}'."
            }

        elif session.step == UpdateNodeSteps.RESOLVE_NODE.value:
            try:
                matched_nodes = self.graph_helper_fxns.find_nodes_by_property(
                    graph_name=session.graph_name,
                    property_key=session.known_property_key,
                    property_value=session.known_property_value
                )

                if not matched_nodes:
                    bad_value = session.known_property_value
                    session.known_property_value = None
                    return {
                        "status": "no_matching_node",
                        "message": f"No node found where {session.known_property_key} = {bad_value}. Please provide another value.",
                        "matched_nodes": []
                    }

                if len(matched_nodes) > 1:
                    bad_value = session.known_property_value
                    session.known_property_value = None
                    return {
                        "status": "multiple_matching_nodes",
                        "message": f"Multiple nodes matched where {session.known_property_key} = {bad_value}. Please provide a more specific property key or a more specific value.",
                        "matched_nodes": matched_nodes
                    }

                resolved_node = matched_nodes[0]
                session.resolved_node_id = resolved_node["node_id"]
                session.resolved_node_preview = resolved_node

                current_properties = resolved_node.get("properties", {})
                available_properties = list(current_properties.keys()) if current_properties else []

                return {
                    "status": "node_resolved",
                    "message": "Matching node found. Please provide the properties you want to update as a dictionary.",
                    "resolved_node": resolved_node,
                    "available_properties": available_properties
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        elif session.step == UpdateNodeSteps.ASK_PROPERTIES_TO_UPDATE.value:
            try:
                node_preview = self.graph_helper_fxns.get_node_by_id(
                    graph_name=session.graph_name,
                    node_id=session.resolved_node_id
                )

                available_properties = []
                if node_preview and node_preview.get("properties"):
                    available_properties = list(node_preview["properties"].keys())

                return {
                    "status": "ask_properties_to_update",
                    "message": "Please provide the properties you want to update as a dictionary.",
                    "resolved_node": node_preview if node_preview else {},
                    "available_properties": available_properties
                }
            except Exception as e:
                return {
                    "status": "ask_properties_to_update",
                    "message": "Please provide the properties you want to update as a dictionary.",
                    "resolved_node": {},
                    "available_properties": [],
                    "warning": str(e)
                }

        elif session.step == UpdateNodeSteps.USER_CONFIRMATION.value:
            try:
                node_preview = self.graph_helper_fxns.get_node_by_id(
                    graph_name=session.graph_name,
                    node_id=session.resolved_node_id
                )

                return {
                    "status": "update_summary",
                    "message": f"Update this node in graph '{session.graph_name}' with properties {session.properties_to_update}?",
                    "resolved_node": node_preview if node_preview else {}
                }
            except Exception as e:
                return {
                    "status": "update_summary",
                    "message": f"Update this node in graph '{session.graph_name}' with properties {session.properties_to_update}?",
                    "resolved_node": {},
                    "warning": str(e)
                }

        elif session.step == UpdateNodeSteps.UPDATE_NODE.value:
            if not session.user_confirmation:
                UPDATENODESESSIONS.pop(session.session_id, None)
                return {
                    "status": "cancelled",
                    "message": "Node update cancelled by the user."
                }

            try:
                result = self.graph_helper_fxns.update_node_properties(
                    graph_name=session.graph_name,
                    node_id=session.resolved_node_id,
                    properties=session.properties_to_update or {}
                )

                if not result:
                    session.resolved_node_id = None
                    session.resolved_node_preview = None
                    session.step = UpdateNodeSteps.ASK_KNOWN_PROPERTY_VALUE.value
                    return {
                        "status": "error, call the tool again with correct details",
                        "message": "The resolved node could not be updated."
                    }

                UPDATENODESESSIONS.pop(session.session_id, None)
                return {
                    "status": "node_updated",
                    "message": "Node properties updated successfully.",
                    "data": result
                }

            except Exception as e:
                session.properties_to_update = None
                session.step = UpdateNodeSteps.ASK_PROPERTIES_TO_UPDATE.value
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        else:
            UPDATENODESESSIONS.pop(session.session_id, None)
            return {
                "status": "completed",
                "message": "Update node process completed."
            }

    def create_relationship(self, session_state: SessionStateForCreateRelationship) -> Dict[str, Any]:

        def decide_step(s: SessionStateForCreateRelationship) -> str:
            has_graph_name = bool((s.graph_name or "").strip())

            has_source_known_property_key = bool((s.source_known_property_key or "").strip())
            has_source_known_property_value = s.source_known_property_value is not None
            has_source_node_id = bool((s.source_node_id or "").strip())

            has_target_known_property_key = bool((s.target_known_property_key or "").strip())
            has_target_known_property_value = s.target_known_property_value is not None
            has_target_node_id = bool((s.target_node_id or "").strip())

            has_relationship_type = bool((s.relationship_type or "").strip())
            has_properties = s.properties is not None
            has_confirmation = s.user_confirmation is not None

            if not has_graph_name:
                return CreateRelationshipSteps.ASK_GRAPH_NAME.value

            if has_graph_name and not has_source_known_property_key:
                return CreateRelationshipSteps.ASK_SOURCE_PROPERTY_KEY.value
            if has_graph_name and has_source_known_property_key and not has_source_known_property_value:
                return CreateRelationshipSteps.ASK_SOURCE_PROPERTY_VALUE.value
            if has_graph_name and has_source_known_property_key and has_source_known_property_value and not has_source_node_id:
                return CreateRelationshipSteps.RESOLVE_SOURCE_NODE.value

            if has_source_node_id and not has_target_known_property_key:
                return CreateRelationshipSteps.ASK_TARGET_PROPERTY_KEY.value
            if has_source_node_id and has_target_known_property_key and not has_target_known_property_value:
                return CreateRelationshipSteps.ASK_TARGET_PROPERTY_VALUE.value
            if has_source_node_id and has_target_known_property_key and has_target_known_property_value and not has_target_node_id:
                return CreateRelationshipSteps.RESOLVE_TARGET_NODE.value

            if has_source_node_id and has_target_node_id and not has_relationship_type:
                return CreateRelationshipSteps.ASK_RELATIONSHIP_TYPE.value
            if has_source_node_id and has_target_node_id and has_relationship_type and not has_properties:
                return CreateRelationshipSteps.ASK_PROPERTIES.value
            if has_source_node_id and has_target_node_id and has_relationship_type and has_properties and not has_confirmation:
                return CreateRelationshipSteps.USER_CONFIRMATION.value

            return CreateRelationshipSteps.CREATE_RELATIONSHIP.value

        session = CREATERELATIONSHIPSESSIONS.setdefault(session_state.session_id, session_state)

        if session_state.graph_name is not None:
            session.graph_name = session_state.graph_name

        if session_state.source_known_property_key is not None:
            session.source_known_property_key = session_state.source_known_property_key
        if session_state.source_known_property_value is not None:
            session.source_known_property_value = session_state.source_known_property_value
        if session_state.source_node_id is not None:
            session.source_node_id = session_state.source_node_id
        if session_state.source_node_preview is not None:
            session.source_node_preview = session_state.source_node_preview

        if session_state.target_known_property_key is not None:
            session.target_known_property_key = session_state.target_known_property_key
        if session_state.target_known_property_value is not None:
            session.target_known_property_value = session_state.target_known_property_value
        if session_state.target_node_id is not None:
            session.target_node_id = session_state.target_node_id
        if session_state.target_node_preview is not None:
            session.target_node_preview = session_state.target_node_preview

        if session_state.relationship_type is not None:
            session.relationship_type = session_state.relationship_type
        if session_state.properties is not None:
            session.properties = session_state.properties
        if session_state.user_confirmation is not None:
            session.user_confirmation = session_state.user_confirmation

        session.step = decide_step(session)

        if session.step == CreateRelationshipSteps.ASK_GRAPH_NAME.value:
            try:
                available_graphs = self.graph_helper_fxns.get_available_graphs()
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

        elif session.step == CreateRelationshipSteps.ASK_SOURCE_PROPERTY_KEY.value:
            try:
                available_property_keys = self.graph_helper_fxns.get_all_node_property_keys(session.graph_name)
                return {
                    "status": "ask_source_property_key",
                    "message": "These are the available node property keys in the graph. Please tell me which property key you know for the source node.",
                    "available_property_keys": available_property_keys
                }
            except Exception as e:
                return {
                    "status": "ask_source_property_key",
                    "message": "Please provide the property key you know for the source node.",
                    "available_property_keys": [],
                    "warning": str(e)
                }

        elif session.step == CreateRelationshipSteps.ASK_SOURCE_PROPERTY_VALUE.value:
            return {
                "status": "ask_source_property_value",
                "message": f"Please provide the value for source node property key '{session.source_known_property_key}'."
            }

        elif session.step == CreateRelationshipSteps.RESOLVE_SOURCE_NODE.value:
            try:
                matched_nodes = self.graph_helper_fxns.find_nodes_by_property(
                    graph_name=session.graph_name,
                    property_key=session.source_known_property_key,
                    property_value=session.source_known_property_value
                )

                if not matched_nodes:
                    bad_value = session.source_known_property_value
                    session.source_known_property_value = None
                    return {
                        "status": "no_matching_source_node",
                        "message": f"No source node found where {session.source_known_property_key} = {bad_value}. Please provide another value.",
                        "matched_nodes": []
                    }

                if len(matched_nodes) > 1:
                    bad_value = session.source_known_property_value
                    session.source_known_property_value = None
                    return {
                        "status": "multiple_matching_source_nodes",
                        "message": f"Multiple source nodes matched where {session.source_known_property_key} = {bad_value}. Please provide a more specific property key or value.",
                        "matched_nodes": matched_nodes
                    }

                resolved_node = matched_nodes[0]
                session.source_node_id = resolved_node["node_id"]
                session.source_node_preview = resolved_node

                return {
                    "status": "source_node_resolved",
                    "message": "Source node resolved successfully. Now provide the property key you know for the target node.",
                    "resolved_source_node": resolved_node
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        elif session.step == CreateRelationshipSteps.ASK_TARGET_PROPERTY_KEY.value:
            try:
                available_property_keys = self.graph_helper_fxns.get_all_node_property_keys(session.graph_name)
                return {
                    "status": "ask_target_property_key",
                    "message": "These are the available node property keys in the graph. Please tell me which property key you know for the target node.",
                    "available_property_keys": available_property_keys,
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {}
                }
            except Exception as e:
                return {
                    "status": "ask_target_property_key",
                    "message": "Please provide the property key you know for the target node.",
                    "available_property_keys": [],
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "warning": str(e)
                }

        elif session.step == CreateRelationshipSteps.ASK_TARGET_PROPERTY_VALUE.value:
            return {
                "status": "ask_target_property_value",
                "message": f"Please provide the value for target node property key '{session.target_known_property_key}'.",
                "resolved_source_node": session.source_node_preview if session.source_node_preview else {}
            }

        elif session.step == CreateRelationshipSteps.RESOLVE_TARGET_NODE.value:
            try:
                matched_nodes = self.graph_helper_fxns.find_nodes_by_property(
                    graph_name=session.graph_name,
                    property_key=session.target_known_property_key,
                    property_value=session.target_known_property_value
                )

                if not matched_nodes:
                    bad_value = session.target_known_property_value
                    session.target_known_property_value = None
                    return {
                        "status": "no_matching_target_node",
                        "message": f"No target node found where {session.target_known_property_key} = {bad_value}. Please provide another value.",
                        "matched_nodes": [],
                        "resolved_source_node": session.source_node_preview if session.source_node_preview else {}
                    }

                if len(matched_nodes) > 1:
                    bad_value = session.target_known_property_value
                    session.target_known_property_value = None
                    return {
                        "status": "multiple_matching_target_nodes",
                        "message": f"Multiple target nodes matched where {session.target_known_property_key} = {bad_value}. Please provide a more specific property key or value.",
                        "matched_nodes": matched_nodes,
                        "resolved_source_node": session.source_node_preview if session.source_node_preview else {}
                    }

                resolved_node = matched_nodes[0]
                session.target_node_id = resolved_node["node_id"]
                session.target_node_preview = resolved_node

                return {
                    "status": "target_node_resolved",
                    "message": "Target node resolved successfully. Please provide the relationship type.",
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": resolved_node
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        elif session.step == CreateRelationshipSteps.ASK_RELATIONSHIP_TYPE.value:
            try:
                available_relationship_types = self.graph_helper_fxns.get_available_relationship_types(session.graph_name)
                return {
                    "status": "ask_relationship_type",
                    "message": "Please provide the relationship type.",
                    "available_relationship_types": available_relationship_types,
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": session.target_node_preview if session.target_node_preview else {}
                }
            except Exception as e:
                return {
                    "status": "ask_relationship_type",
                    "message": "Please provide the relationship type.",
                    "available_relationship_types": [],
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": session.target_node_preview if session.target_node_preview else {},
                    "warning": str(e)
                }

        elif session.step == CreateRelationshipSteps.ASK_PROPERTIES.value:
            try:
                available_properties = self.graph_helper_fxns.get_relationship_property_keys(
                    graph_name=session.graph_name,
                    relationship_type=session.relationship_type
                )
                return {
                    "status": "ask_properties",
                    "message": "Please provide the relationship properties as a dictionary. Use {} if no properties are needed.",
                    "available_properties": available_properties,
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": session.target_node_preview if session.target_node_preview else {}
                }
            except Exception as e:
                return {
                    "status": "ask_properties",
                    "message": "Please provide the relationship properties as a dictionary. Use {} if no properties are needed.",
                    "available_properties": [],
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": session.target_node_preview if session.target_node_preview else {},
                    "warning": str(e)
                }

        elif session.step == CreateRelationshipSteps.USER_CONFIRMATION.value:
            return {
                "status": "relationship_summary",
                "message": f"Create relationship '{session.relationship_type}' between the resolved source node and resolved target node in graph '{session.graph_name}' with properties {session.properties}?",
                "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                "resolved_target_node": session.target_node_preview if session.target_node_preview else {}
            }

        elif session.step == CreateRelationshipSteps.CREATE_RELATIONSHIP.value:
            if not session.user_confirmation:
                CREATERELATIONSHIPSESSIONS.pop(session.session_id, None)
                return {
                    "status": "cancelled",
                    "message": "Relationship creation cancelled by the user."
                }

            try:
                result = self.graph_helper_fxns.create_relationship(
                    graph_name=session.graph_name,
                    source_node_id=session.source_node_id,
                    target_node_id=session.target_node_id,
                    relationship_type=session.relationship_type,
                    properties=session.properties or {}
                )

                if not result:
                    session.source_node_id = None
                    session.target_node_id = None
                    session.source_node_preview = None
                    session.target_node_preview = None
                    session.step = CreateRelationshipSteps.ASK_SOURCE_PROPERTY_KEY.value
                    return {
                        "status": "error, call the tool again with correct details",
                        "message": "The relationship could not be created because the resolved source or target node was not found."
                    }

                CREATERELATIONSHIPSESSIONS.pop(session.session_id, None)
                return {
                    "status": "relationship_created",
                    "message": "Relationship created successfully.",
                    "data": result
                }

            except Exception as e:
                session.relationship_type = None
                session.step = CreateRelationshipSteps.ASK_RELATIONSHIP_TYPE.value
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        else:
            CREATERELATIONSHIPSESSIONS.pop(session.session_id, None)
            return {
                "status": "completed",
                "message": "Create relationship process completed."
            }

    def delete_relationship(self, session_state: SessionStateForDeleteRelationship) -> Dict[str, Any]:

        def decide_step(s: SessionStateForDeleteRelationship) -> str:
            has_graph_name = bool((s.graph_name or "").strip())

            has_source_known_property_key = bool((s.source_known_property_key or "").strip())
            has_source_known_property_value = s.source_known_property_value is not None
            has_source_node_id = bool((s.source_node_id or "").strip())

            has_target_known_property_key = bool((s.target_known_property_key or "").strip())
            has_target_known_property_value = s.target_known_property_value is not None
            has_target_node_id = bool((s.target_node_id or "").strip())

            has_relationship_type = bool((s.relationship_type or "").strip())
            has_confirmation = s.user_confirmation is not None

            if not has_graph_name:
                return DeleteRelationshipSteps.ASK_GRAPH_NAME.value

            if has_graph_name and not has_source_known_property_key:
                return DeleteRelationshipSteps.ASK_SOURCE_PROPERTY_KEY.value
            if has_graph_name and has_source_known_property_key and not has_source_known_property_value:
                return DeleteRelationshipSteps.ASK_SOURCE_PROPERTY_VALUE.value
            if has_graph_name and has_source_known_property_key and has_source_known_property_value and not has_source_node_id:
                return DeleteRelationshipSteps.RESOLVE_SOURCE_NODE.value

            if has_source_node_id and not has_target_known_property_key:
                return DeleteRelationshipSteps.ASK_TARGET_PROPERTY_KEY.value
            if has_source_node_id and has_target_known_property_key and not has_target_known_property_value:
                return DeleteRelationshipSteps.ASK_TARGET_PROPERTY_VALUE.value
            if has_source_node_id and has_target_known_property_key and has_target_known_property_value and not has_target_node_id:
                return DeleteRelationshipSteps.RESOLVE_TARGET_NODE.value

            if has_source_node_id and has_target_node_id and not has_relationship_type:
                return DeleteRelationshipSteps.ASK_RELATIONSHIP_TYPE.value
            if has_source_node_id and has_target_node_id and has_relationship_type and not has_confirmation:
                return DeleteRelationshipSteps.USER_CONFIRMATION.value

            return DeleteRelationshipSteps.DELETE_RELATIONSHIP.value

        session = DELETERELATIONSHIPSESSIONS.setdefault(session_state.session_id, session_state)

        if session_state.graph_name is not None:
            session.graph_name = session_state.graph_name

        if session_state.source_known_property_key is not None:
            session.source_known_property_key = session_state.source_known_property_key
        if session_state.source_known_property_value is not None:
            session.source_known_property_value = session_state.source_known_property_value
        if session_state.source_node_id is not None:
            session.source_node_id = session_state.source_node_id
        if session_state.source_node_preview is not None:
            session.source_node_preview = session_state.source_node_preview

        if session_state.target_known_property_key is not None:
            session.target_known_property_key = session_state.target_known_property_key
        if session_state.target_known_property_value is not None:
            session.target_known_property_value = session_state.target_known_property_value
        if session_state.target_node_id is not None:
            session.target_node_id = session_state.target_node_id
        if session_state.target_node_preview is not None:
            session.target_node_preview = session_state.target_node_preview

        if session_state.relationship_type is not None:
            session.relationship_type = session_state.relationship_type
        if session_state.user_confirmation is not None:
            session.user_confirmation = session_state.user_confirmation

        session.step = decide_step(session)

        if session.step == DeleteRelationshipSteps.ASK_GRAPH_NAME.value:
            try:
                available_graphs = self.graph_helper_fxns.get_available_graphs()
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

        elif session.step == DeleteRelationshipSteps.ASK_SOURCE_PROPERTY_KEY.value:
            try:
                available_property_keys = self.graph_helper_fxns.get_all_node_property_keys(session.graph_name)
                return {
                    "status": "ask_source_property_key",
                    "message": "These are the available node property keys in the graph. Please tell me which property key you know for the source node.",
                    "available_property_keys": available_property_keys
                }
            except Exception as e:
                return {
                    "status": "ask_source_property_key",
                    "message": "Please provide the property key you know for the source node.",
                    "available_property_keys": [],
                    "warning": str(e)
                }

        elif session.step == DeleteRelationshipSteps.ASK_SOURCE_PROPERTY_VALUE.value:
            return {
                "status": "ask_source_property_value",
                "message": f"Please provide the value for source node property key '{session.source_known_property_key}'."
            }

        elif session.step == DeleteRelationshipSteps.RESOLVE_SOURCE_NODE.value:
            try:
                matched_nodes = self.graph_helper_fxns.find_nodes_by_property(
                    graph_name=session.graph_name,
                    property_key=session.source_known_property_key,
                    property_value=session.source_known_property_value
                )

                if not matched_nodes:
                    bad_value = session.source_known_property_value
                    session.source_known_property_value = None
                    return {
                        "status": "no_matching_source_node",
                        "message": f"No source node found where {session.source_known_property_key} = {bad_value}. Please provide another value.",
                        "matched_nodes": []
                    }

                if len(matched_nodes) > 1:
                    bad_value = session.source_known_property_value
                    session.source_known_property_value = None
                    return {
                        "status": "multiple_matching_source_nodes",
                        "message": f"Multiple source nodes matched where {session.source_known_property_key} = {bad_value}. Please provide a more specific property key or value.",
                        "matched_nodes": matched_nodes
                    }

                resolved_node = matched_nodes[0]
                session.source_node_id = resolved_node["node_id"]
                session.source_node_preview = resolved_node

                return {
                    "status": "source_node_resolved",
                    "message": "Source node resolved successfully. Now provide the property key you know for the target node.",
                    "resolved_source_node": resolved_node
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        elif session.step == DeleteRelationshipSteps.ASK_TARGET_PROPERTY_KEY.value:
            try:
                available_property_keys = self.graph_helper_fxns.get_all_node_property_keys(session.graph_name)
                return {
                    "status": "ask_target_property_key",
                    "message": "These are the available node property keys in the graph. Please tell me which property key you know for the target node.",
                    "available_property_keys": available_property_keys,
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {}
                }
            except Exception as e:
                return {
                    "status": "ask_target_property_key",
                    "message": "Please provide the property key you know for the target node.",
                    "available_property_keys": [],
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "warning": str(e)
                }

        elif session.step == DeleteRelationshipSteps.ASK_TARGET_PROPERTY_VALUE.value:
            return {
                "status": "ask_target_property_value",
                "message": f"Please provide the value for target node property key '{session.target_known_property_key}'.",
                "resolved_source_node": session.source_node_preview if session.source_node_preview else {}
            }

        elif session.step == DeleteRelationshipSteps.RESOLVE_TARGET_NODE.value:
            try:
                matched_nodes = self.graph_helper_fxns.find_nodes_by_property(
                    graph_name=session.graph_name,
                    property_key=session.target_known_property_key,
                    property_value=session.target_known_property_value
                )

                if not matched_nodes:
                    bad_value = session.target_known_property_value
                    session.target_known_property_value = None
                    return {
                        "status": "no_matching_target_node",
                        "message": f"No target node found where {session.target_known_property_key} = {bad_value}. Please provide another value.",
                        "matched_nodes": [],
                        "resolved_source_node": session.source_node_preview if session.source_node_preview else {}
                    }

                if len(matched_nodes) > 1:
                    bad_value = session.target_known_property_value
                    session.target_known_property_value = None
                    return {
                        "status": "multiple_matching_target_nodes",
                        "message": f"Multiple target nodes matched where {session.target_known_property_key} = {bad_value}. Please provide a more specific property key or value.",
                        "matched_nodes": matched_nodes,
                        "resolved_source_node": session.source_node_preview if session.source_node_preview else {}
                    }

                resolved_node = matched_nodes[0]
                session.target_node_id = resolved_node["node_id"]
                session.target_node_preview = resolved_node

                return {
                    "status": "target_node_resolved",
                    "message": "Target node resolved successfully. Please provide the relationship type to delete.",
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": resolved_node
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        elif session.step == DeleteRelationshipSteps.ASK_RELATIONSHIP_TYPE.value:
            try:
                available_relationship_types = self.graph_helper_fxns.get_available_relationship_types(session.graph_name)
                return {
                    "status": "ask_relationship_type",
                    "message": "Please provide the relationship type to delete.",
                    "available_relationship_types": available_relationship_types,
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": session.target_node_preview if session.target_node_preview else {}
                }
            except Exception as e:
                return {
                    "status": "ask_relationship_type",
                    "message": "Please provide the relationship type to delete.",
                    "available_relationship_types": [],
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": session.target_node_preview if session.target_node_preview else {},
                    "warning": str(e)
                }

        elif session.step == DeleteRelationshipSteps.USER_CONFIRMATION.value:
            try:
                relationship_preview = self.graph_helper_fxns.preview_relationship_for_delete(
                    graph_name=session.graph_name,
                    source_node_id=session.source_node_id,
                    target_node_id=session.target_node_id,
                    relationship_type=session.relationship_type
                )
                return {
                    "status": "delete_relationship_summary",
                    "message": f"Delete relationship '{session.relationship_type}' between the resolved source node and resolved target node in graph '{session.graph_name}'?",
                    "relationship_preview": relationship_preview if relationship_preview else {},
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": session.target_node_preview if session.target_node_preview else {}
                }
            except Exception as e:
                return {
                    "status": "delete_relationship_summary",
                    "message": f"Delete relationship '{session.relationship_type}' between the resolved source node and resolved target node in graph '{session.graph_name}'?",
                    "relationship_preview": {},
                    "resolved_source_node": session.source_node_preview if session.source_node_preview else {},
                    "resolved_target_node": session.target_node_preview if session.target_node_preview else {},
                    "warning": str(e)
                }

        elif session.step == DeleteRelationshipSteps.DELETE_RELATIONSHIP.value:
            if not session.user_confirmation:
                DELETERELATIONSHIPSESSIONS.pop(session.session_id, None)
                return {
                    "status": "cancelled",
                    "message": "Relationship deletion cancelled by the user."
                }

            try:
                result = self.graph_helper_fxns.delete_relationship_with_confirmation(
                    graph_name=session.graph_name,
                    source_node_id=session.source_node_id,
                    target_node_id=session.target_node_id,
                    relationship_type=session.relationship_type
                )

                if not result:
                    session.source_node_id = None
                    session.target_node_id = None
                    session.source_node_preview = None
                    session.target_node_preview = None
                    session.relationship_type = None
                    session.step = DeleteRelationshipSteps.ASK_SOURCE_PROPERTY_KEY.value
                    return {
                        "status": "error, call the tool again with correct details",
                        "message": "No matching relationship found."
                    }

                DELETERELATIONSHIPSESSIONS.pop(session.session_id, None)
                return {
                    "status": "relationship_deleted",
                    "message": "Relationship deleted successfully.",
                    "data": result
                }

            except Exception as e:
                return {
                    "status": "error, call the tool again with correct details",
                    "message": str(e)
                }

        else:
            DELETERELATIONSHIPSESSIONS.pop(session.session_id, None)
            return {
                "status": "completed",
                "message": "Delete relationship process completed."
            }
