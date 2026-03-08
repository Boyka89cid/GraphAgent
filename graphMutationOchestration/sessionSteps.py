from enum import Enum

class CreateNodeSteps(Enum):
    ASK_GRAPH_NAME = "ask_graph_name"
    ASK_LABELS = "ask_labels"
    ASK_PROPERTIES = "ask_properties"
    USER_CONFIRMATION = "user_confirmation"
    CREATE_NODE = "create_node"


class UpdateNodeSteps(Enum):
    ASK_GRAPH_NAME = "ask_graph_name"
    ASK_KNOWN_PROPERTY_KEY = "ask_known_property_key"
    ASK_KNOWN_PROPERTY_VALUE = "ask_known_property_value"
    RESOLVE_NODE = "resolve_node"
    ASK_PROPERTIES_TO_UPDATE = "ask_properties_to_update"
    USER_CONFIRMATION = "user_confirmation"
    UPDATE_NODE = "update_node"


class DeleteNodeSteps(Enum):
    ASK_GRAPH_NAME = "ask_graph_name"
    ASK_KNOWN_PROPERTY_KEY = "ask_known_property_key"
    ASK_KNOWN_PROPERTY_VALUE = "ask_known_property_value"
    RESOLVE_NODE = "resolve_node"
    USER_CONFIRMATION = "user_confirmation"
    DELETE_NODE = "delete_node"


class CreateRelationshipSteps(Enum):
    ASK_GRAPH_NAME = "ask_graph_name"
    ASK_SOURCE_PROPERTY_KEY = "ask_source_property_key"
    ASK_SOURCE_PROPERTY_VALUE = "ask_source_property_value"
    RESOLVE_SOURCE_NODE = "resolve_source_node"
    ASK_TARGET_PROPERTY_KEY = "ask_target_property_key"
    ASK_TARGET_PROPERTY_VALUE = "ask_target_property_value"
    RESOLVE_TARGET_NODE = "resolve_target_node"
    ASK_RELATIONSHIP_TYPE = "ask_relationship_type"
    ASK_PROPERTIES = "ask_properties"
    USER_CONFIRMATION = "user_confirmation"
    CREATE_RELATIONSHIP = "create_relationship"


class DeleteRelationshipSteps(Enum):
    ASK_GRAPH_NAME = "ask_graph_name"
    ASK_SOURCE_PROPERTY_KEY = "ask_source_property_key"
    ASK_SOURCE_PROPERTY_VALUE = "ask_source_property_value"
    RESOLVE_SOURCE_NODE = "resolve_source_node"
    ASK_TARGET_PROPERTY_KEY = "ask_target_property_key"
    ASK_TARGET_PROPERTY_VALUE = "ask_target_property_value"
    RESOLVE_TARGET_NODE = "resolve_target_node"
    ASK_RELATIONSHIP_TYPE = "ask_relationship_type"
    USER_CONFIRMATION = "user_confirmation"
    DELETE_RELATIONSHIP = "delete_relationship"