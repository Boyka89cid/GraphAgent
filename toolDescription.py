class ToolsDescription:
    """
    This class contains descriptions for the tools used in the LLM Router Tools.
    Each attribute represents a tool and its corresponding description.
    """

    # Tool descriptions for LLM Router Tools
    check_neo4j_connection = "This tool allows you to interact with a Neo4j graph database. You can execute Cypher queries to retrieve or manipulate data within the database."
    show_all_databases = "This tool retrieves and displays all databases available in the connected Neo4j instance, excluding the system database."

class ToolPrompts:
    """
    This class contains prompt templates for the tools used in the LLM Router Tools.
    Each attribute represents a tool and its corresponding prompt template.
    """

    # Prompt templates for LLM Router Tools
    check_neo4j_connection = "Please check the connectivity to the Neo4j database before starting the process of retrieving or manipulating data."
    show_all_databases = "Please count all databases in the connected Neo4j instance whenever show all databases is requested or required, excluding the system database."