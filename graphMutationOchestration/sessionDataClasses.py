from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from graphMutationOchestration.sessionSteps import (
    CreateNodeSteps,
    CreateRelationshipSteps,
    DeleteNodeSteps,
    DeleteRelationshipSteps,
    UpdateNodeSteps
)

@dataclass
class SessionStateForCreateNode:
    session_id: str
    graph_name: Optional[str] = None
    labels: Optional[List[str]] = None
    properties: Optional[Dict[str, Any]] = None
    user_confirmation: Optional[bool] = None
    step: str = CreateNodeSteps.ASK_GRAPH_NAME.value


@dataclass
class SessionStateForUpdateNode:
    session_id: str
    graph_name: Optional[str] = None
    known_property_key: Optional[str] = None
    known_property_value: Optional[Any] = None
    resolved_node_id: Optional[str] = None
    resolved_node_preview: Optional[Dict[str, Any]] = None
    properties_to_update: Optional[Dict[str, Any]] = None
    user_confirmation: Optional[bool] = None
    step: str = UpdateNodeSteps.ASK_GRAPH_NAME.value


@dataclass
class SessionStateForDeleteNode:
    session_id: str
    graph_name: Optional[str] = None
    known_property_key: Optional[str] = None
    known_property_value: Optional[Any] = None
    resolved_node_id: Optional[str] = None
    resolved_node_preview: Optional[Dict[str, Any]] = None
    user_confirmation: Optional[bool] = None
    step: str = DeleteNodeSteps.ASK_GRAPH_NAME.value


@dataclass
class SessionStateForCreateRelationship:
    session_id: str
    graph_name: Optional[str] = None

    source_known_property_key: Optional[str] = None
    source_known_property_value: Optional[Any] = None
    source_node_id: Optional[str] = None
    source_node_preview: Optional[Dict[str, Any]] = None

    target_known_property_key: Optional[str] = None
    target_known_property_value: Optional[Any] = None
    target_node_id: Optional[str] = None
    target_node_preview: Optional[Dict[str, Any]] = None

    relationship_type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    user_confirmation: Optional[bool] = None
    step: str = CreateRelationshipSteps.ASK_GRAPH_NAME.value


@dataclass
class SessionStateForDeleteRelationship:
    session_id: str
    graph_name: Optional[str] = None

    source_known_property_key: Optional[str] = None
    source_known_property_value: Optional[Any] = None
    source_node_id: Optional[str] = None
    source_node_preview: Optional[Dict[str, Any]] = None

    target_known_property_key: Optional[str] = None
    target_known_property_value: Optional[Any] = None
    target_node_id: Optional[str] = None
    target_node_preview: Optional[Dict[str, Any]] = None

    relationship_type: Optional[str] = None
    user_confirmation: Optional[bool] = None
    step: str = DeleteRelationshipSteps.ASK_GRAPH_NAME.value