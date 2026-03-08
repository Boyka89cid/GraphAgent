class InspectionToolPrompts:
    RULES = '''
    - You can skip a single or multiple steps if you already have the required information. For example, if you already have the table_type, you can skip the ask_table_type step. However, you cannot skip a step or steps if the required information is missing.
    - Respond ONLY with a tool call.
    - Do NOT include any natural-language explanation before the tool call.
    - After the tool returns, you may present exactly the tool's message verbatim.
    - If you see multiple select options in any step of workflow, use your ask_user_input_v0 widget to ask user to select one of the options. For example, if you have 3 table types to select from, use ask_user_input_v0 with those 3 options as input.
    - If their are more than 3 options are available which are short in text (max 20 characters) for the human-in-the-loop process, select any 3 options to present to the user in ask_user_input_v0 widget. After user selects one of the 3 options, present the next 3 options and so on until all options are presented. You can use the same ask_user_input_v0 widget to present all options in this way.
    - Do NOT call the final tool unless you have all the required information and user_confirmation=true.
    '''
    
    graph_node_count_workflow = f'''
    WORKFLOW: graph_node_count_workflow
    State fields:
    - session_id: string (required).
    - steps : [ask_graph_name, get_graph_node_count]
    - graph_name: string (required for get_graph_node_count step)
    - node_count: int (output of get_graph_node_count step)
    - relationship_count: int (output of get_graph_node_count step)
    {RULES}
    Steps:
    1) ask_graph_name: Ask for the graph name if not provided. Output: graph_name.
    2) get_graph_node_count: Get the count of nodes and relationships in the graph. Requires graph_name. Output: node_count, relationship_count.
    '''
    graph_nodes_count = f'Orchestrate the process of counting nodes in Neo4j using the {graph_node_count_workflow} workflow.'

    count_nodes_by_label_workflow = f'''
    WORKFLOW: count_nodes_by_label_workflow
    State fields:
    - session_id: string (required).
    - steps : [ask_graph_name, ask_node_label, get_nodes_count_by_label]
    - graph_name: string (required for ask_node_label and get_nodes_count_by_label steps)
    - node_label: string (required for get_nodes_count_by_label step)
    - node_count: int (output of get_nodes_count_by_label step)
    {RULES}
    Steps:
    1) ask_graph_name: Ask for the graph name if not provided. Output: graph_name.
    2) ask_node_label: Ask for the node label if not provided. Requires graph_name. Output: node_label.
    3) get_nodes_count_by_label: Get the count of nodes for the given node label in the graph. Requires graph_name and node_label. Output: node_count.
    '''
    count_nodes_by_label = f'Orchestrate the process of counting nodes by label in Neo4j using the {count_nodes_by_label_workflow} workflow.'

    count_relationships_by_type_workflow = f'''
    WORKFLOW: count_relationships_by_type_workflow
    State fields:
    - session_id: string (required).
    - steps : [ask_graph_name, ask_relationship_type, get_relationships_count_by_type]
    - graph_name: string (required for ask_relationship_type and get_relationships_count_by_type steps)
    - relationship_type: string (required for get_relationships_count_by_type step)
    - relationship_count: int (output of get_relationships_count_by_type step)
    {RULES} 
    Steps:
    1) ask_graph_name: Ask for the graph name if not provided. Output: graph_name.
    2) ask_relationship_type: Ask for the relationship type if not provided. Requires graph_name. Output: relationship_type.
    3) get_relationships_count_by_type: Get the count of relationships for the given relationship type in the graph. Requires graph_name and relationship_type. Output: relationship_count.
    '''
    count_relationships_by_type = f'Orchestrate the process of counting relationships by type in Neo4j using the {count_relationships_by_type_workflow} workflow.'