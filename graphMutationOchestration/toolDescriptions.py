class OrchestrationToolPrompts:

    RULES = '''
    - You can skip a single or multiple steps if you already have the required information. For example, if you already have the table_type, you can skip the ask_table_type step. However, you cannot skip a step or steps if the required information is missing.
    - Respond ONLY with a tool call.
    - Do NOT include any natural-language explanation before the tool call.
    - After the tool returns, you may present exactly the tool's message verbatim.
    - If you see multiple select options in any step of workflow, use your ask_user_input_v0 widget to ask user to select one of the options. For example, if you have 3 table types to select from, use ask_user_input_v0 with those 3 options as input.
    - If their are more than 3 options are available which are short in text (max 20 characters) for the human-in-the-loop process, select any 3 options to present to the user in ask_user_input_v0 widget. After user selects one of the 3 options, present the next 3 options and so on until all options are presented. You can use the same ask_user_input_v0 widget to present all options in this way.
    - Do NOT call the final tool unless you have all the required information and user_confirmation=true.
    '''

    create_node_workflow = f'''
    WORKFLOW: create_node_workflow
    State fields:
    - session_id: string (required).
    - steps: enum [ask_graph_name, ask_node_label, ask_properties, user_confirmation]
    - graph_name: string 
    - node_label: string
    - properties: dictionary
    - user_confirmation: bool | null
    {RULES}
    Steps:
    1) ask_graph_name: Ask the user for the graph name if it is not already provided in the session state.
    2) ask_node_label: Ask the user for the node label if it is not already provided in the session state.
    3) ask_properties: Ask the user for the properties of the node if they are not already provided in the session state. The properties should be provided as a dictionary.
    4) user_confirmation: Ask the user for confirmation before creating the node. If the user confirms, proceed to create the node in the Neo4j database using the provided graph name, node label, and properties. If the user does not confirm, terminate the workflow without creating the node.
    '''
    create_node = f'Orchestrate the process of creating a node in Neo4j using the {create_node_workflow} workflow.'

    update_node_workflow = f'''
    WORKFLOW: update_node_workflow
    State fields:
    - session_id: string (required).
    - steps: enum [ask_graph_name, ask_node_label, ask_properties, user_confirmation]
    - graph_name: string 
    - known_property_key: string
    - known_property_value: any
    - resolved_node_id: string
    - resolved_node_preview: dictionary
    - properties_to_update: dictionary
    - user_confirmation: bool | null

    {RULES}
    Steps:
    1) ask_graph_name: Ask the user for the graph name if it is not already provided in the session state.
    2) ask_known_property_key: Ask the user for the known property key if it is not already provided in the session state. The known property key is a property key that can be used to uniquely identify the node to be updated.
    3) ask_known_property_value: Ask the user for the known property value if it is not already provided in the session state. The known property value is the value corresponding to the known property key that can be used to uniquely identify the node to be updated.
    4) resolve_node: Use the provided graph name, known property key, and known property value to find the node to be updated in the Neo4j database. If a node is found, store its ID in resolved_node_id and a preview of its properties in resolved_node_preview in the session state. If no node is found, inform the user and terminate the workflow.
    5) ask_properties_to_update: Ask the user for the properties to update if they are not already provided in the session state. The properties to update should be provided as a dictionary.
    6) user_confirmation: Ask the user for confirmation before updating the node. If the user confirms, proceed to update the node in the Neo4j database using the resolved_node_id and the provided properties to update. If the user does not confirm, terminate the workflow without updating the node.
    '''
    update_node = f'Orchestrate the process of updating a node in Neo4j using the {update_node_workflow} workflow.'

    delete_node_workflow = f'''
    WORKFLOW: delete_node_workflow
    State fields:
    - session_id: string (required).
    - steps: enum [ask_graph_name, ask_known_property_key, ask_known_property_value, resolve_node, user_confirmation, delete_node]
    - graph_name: string
    - known_property_key: string
    - known_property_value: any
    - resolved_node_id: string
    - resolved_node_preview: dictionary
    - user_confirmation: bool | null
    {RULES}
    Steps:
    1) ask_graph_name: Ask the user for the graph name if it is not already provided in the session state.
    2) ask_known_property_key: Ask the user for the known property key if it is not already provided in the session state. The known property key is a property key that can be used to uniquely identify the node to be deleted.
    3) ask_known_property_value: Ask the user for the known property value if it is not already provided in the session state. The known property value is the value corresponding to the known property key that can be used to uniquely identify the node to be deleted.
    4) resolve_node: Use the provided graph name, known property key, and known property value to find the node to be deleted in the Neo4j database. If a node is found, store its ID in resolved_node_id and a preview of its properties in resolved_node_preview in the session state. If no node is found, inform the user and terminate the workflow.
    5) user_confirmation: Ask the user for confirmation before deleting the node. If the user confirms, proceed to delete the node in the Neo4j database using the resolved_node_id. If the user does not confirm, terminate the workflow without deleting the node.
    '''

    delete_node = f'Orchestrate the process of deleting a node in Neo4j using the {delete_node_workflow} workflow.'

    create_relationship_workflow = f'''
    WORKFLOW: create_relationship_workflow
    State fields:
    - session_id: string (required).
    - steps: enum [ask_graph_name, ask_source_known_property_key, ask_source_known_property_value, resolve_source_node, ask_target_known_property_key, ask_target_known_property_value, resolve_target_node, ask_relationship_type, ask_properties, user_confirmation, create_relationship]
    - graph_name: string
    - source_known_property_key: string
    - source_known_property_value: any
    - source_node_id: string
    - source_node_preview: dictionary
    - target_known_property_key: string
    - target_known_property_value: any
    - target_node_id: string
    - target_node_preview: dictionary
    - relationship_type: string 

    {RULES}
    Steps:
    1) ask_graph_name: Ask the user for the graph name if it is not already provided in the session state.
    2) ask_source_known_property_key: Ask the user for the source node's known property key if it is not already provided in the session state.
    3) ask_source_known_property_value: Ask the user for the source node's known property value if it is not already provided in the session state.
    4) resolve_source_node: Use the provided graph name, source known property key, and source known property value to find the source node in the Neo4j database. If a node is found, store its ID in source_node_id and a preview of its properties in source_node_preview in the session state. If no node is found, inform the user and terminate the workflow.
    5) ask_target_known_property_key: Ask the user for the target node's known property key if it is not already provided in the session state.
    6) ask_target_known_property_value: Ask the user for the target node's known property value if it is not already provided in the session state.
    7) resolve_target_node: Use the provided graph name, target known property key, and target known property value to find the target node in the Neo4j database. If a node is found, store its ID in target_node_id and a preview of its properties in target_node_preview in the session state. If no node is found, inform the user and terminate the workflow.
    8) ask_relationship_type: Ask the user for the relationship type if it is not already provided in the session state.
    9) ask_properties: Ask the user for the properties of the relationship if they are not already provided in the session state. The properties should be provided as a dictionary.
    10) user_confirmation: Ask the user for confirmation before creating the relationship. If the user confirms, proceed to create the relationship in the Neo4j database using the provided graph name, source node ID, target node ID, relationship type, and properties. If the user does not confirm, terminate the workflow without creating the relationship.
    '''
    create_relationship = f'Orchestrate the process of creating a relationship in Neo4j using the {create_relationship_workflow} workflow.'

    delete_relationship_workflow = f'''
    WORKFLOW: delete_relationship_workflow
    State fields:
    - session_id: string (required).
    - steps: enum [ask_graph_name, ask_source_known_property_key, ask_source_known_property_value, resolve_source_node, ask_target_known_property_key, ask_target_known_property_value, resolve_target_node, ask_relationship_type, user_confirmation, delete_relationship]
    - graph_name: string
    - source_known_property_key: string
    - source_known_property_value: any
    - source_node_id: string
    - source_node_preview: dictionary
    - target_known_property_key: string
    - target_known_property_value: any
    - target_node_id: string
    - target_node_preview: dictionary
    - relationship_type: string
    
    {RULES}
    Steps:
    1) ask_graph_name: Ask the user for the graph name if it is not already provided in the session state.
    2) ask_source_known_property_key: Ask the user for the source node's known property key if it is not already provided in the session state.
    3) ask_source_known_property_value: Ask the user for the source node's known property value if it is not already provided in the session state. 
    4) resolve_source_node: Use the provided graph name, source known property key, and source known property value to find the source node in the Neo4j database. If a node is found, store its ID in source_node_id and a preview of its properties in source_node_preview in the session state. If no node is found, inform the user and terminate the workflow.
    5) ask_target_known_property_key: Ask the user for the target node's known property key if it is not already provided in the session state. 
    6) ask_target_known_property_value: Ask the user for the target node's known property value if it is not already provided in the session state.
    7) resolve_target_node: Use the provided graph name, target known property key, and target known property value to find the target node in the Neo4j database. If a node is found, store its ID in target_node_id and a preview of its properties in target_node_preview in the session state. If no node is found, inform the user and terminate the workflow.
    8) ask_relationship_type: Ask the user for the relationship type if it is not already provided in the session state.
    9) user_confirmation: Ask the user for confirmation before deleting the relationship. If the user confirms, proceed to delete the relationship in the Neo4j database using the provided graph name, source node ID, target node ID, and relationship type. If the user does not confirm, terminate the workflow without deleting the relationship.
    '''
    delete_relationship = f'Orchestrate the process of deleting a relationship in Neo4j using the {delete_relationship_workflow} workflow.'

class ToolPrompts:
    """
    This class contains prompt templates for the tools used in the LLM Router Tools.
    Each attribute represents a tool and its corresponding prompt template.
    """

    # Prompt templates for LLM Router Tools
    check_neo4j_connection = "Please check the connectivity to the Neo4j database before starting the process of retrieving or manipulating data."
    show_all_databases = "Please count all databases in the connected Neo4j instance whenever show all databases is requested or required, excluding the system database."