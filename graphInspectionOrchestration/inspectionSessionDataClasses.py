from dataclasses import dataclass
from typing import Optional, Dict, Any

from graphInspectionOrchestration.inspectionSessionSteps import (
    CountNodesByLabelSteps,
    CountRelationshipsByTypeSteps,
    GraphNodeCountSteps
    )


@dataclass
class SessionStateNodeCountGraph:
    session_id: str
    step: str = GraphNodeCountSteps.ASK_GRAPH_NAME.value
    graph_name: Optional[str] = None
    node_count: int = 0
    relationship_count: int = 0

@dataclass
class SessionStateForCountNodesByLabel:
    session_id: str
    graph_name: Optional[str] = None
    node_label: Optional[str] = None
    step: str = CountNodesByLabelSteps.ASK_GRAPH_NAME.value


@dataclass
class SessionStateForCountRelationshipsByType:
    session_id: str
    graph_name: Optional[str] = None
    relationship_type: Optional[str] = None
    step: str = CountRelationshipsByTypeSteps.ASK_GRAPH_NAME.value