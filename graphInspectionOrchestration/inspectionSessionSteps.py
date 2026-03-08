from enum import Enum

class GraphNodeCountSteps(Enum):
    ASK_GRAPH_NAME = "ask_graph_name"
    GET_GRAPH_NODE_COUNT = "get_graph_node_count"


class CountNodesByLabelSteps(Enum):
    ASK_GRAPH_NAME = "ask_graph_name"
    ASK_NODE_LABEL = "ask_node_label"
    COUNT_NODES_BY_LABEL = "count_nodes_by_label"


class CountRelationshipsByTypeSteps(Enum):
    ASK_GRAPH_NAME = "ask_graph_name"
    ASK_RELATIONSHIP_TYPE = "ask_relationship_type"
    COUNT_RELATIONSHIPS_BY_TYPE = "count_relationships_by_type"