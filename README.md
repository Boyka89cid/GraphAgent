# GraphAgent

GraphAgent is a modular Python framework designed to **inspect and mutate Neo4j graphs using structured Finite State Machine (FSM) orchestration tools**.  
The framework is built to support **LLM-driven agents** that interact with Neo4j safely and deterministically.

GraphAgent separates **graph mutation operations** from **graph inspection operations**, making the system easier to extend, maintain, and integrate with agent-based systems.

---

# Architecture

GraphAgent follows a layered architecture to keep responsibilities separated and maintain clean abstractions.

LLM / Agent  
↓  
Orchestration Tools (FSM Logic)  
↓  
Helper Functions (Cypher Queries)  
↓  
Neo4j Adapter  
↓  
Neo4j Database  

### Layers

**Orchestration Layer**
- Controls tool workflow
- Maintains session state
- Implements FSM steps

**Helper Layer**
- Contains Cypher queries
- Handles database operations
- Performs graph inspection and mutation

**Adapter Layer**
- Handles communication with Neo4j
- Executes Cypher queries
- Returns structured results

---

# Repository Structure

Neo4jAgent/

graphMutationOrchestration/  
- orchestrationTools.py  
- sessionDataClasses.py  
- sessionSteps.py  
- toolDescriptions.py  
- validationHelperFxns.py  

graphInspectionOrchestration/  
- inspectionOrchestrationTools.py  
- inspectionSessionDataClasses.py  
- inspectionSessionSteps.py  
- inspectionHelperFxns.py  
- inspectionToolDescriptions.py  

Other core modules:
- graphHelperFxns.py
- neo4jAdapter.py
- mcpServer.py
- llmRouterTools.py
- config.py

---

# Mutation Tools

Located in:

graphMutationOrchestration/orchestrationTools.py

These tools modify graph data.

## create_node

Creates a node with labels and properties.

Workflow:

graph_name → labels → properties → confirmation → create node

---

## update_node

Updates node properties using property-based identification.

Workflow:

graph_name → property key → property value → resolve node → properties to update → confirmation → update node

---

## delete_node

Deletes a node using detach delete.

Workflow:

graph_name → property key → property value → resolve node → confirmation → delete node

---

## create_relationship

Creates a relationship between two nodes.

Workflow:

graph_name → resolve source node → resolve target node → relationship type → properties → confirmation → create relationship

---

## delete_relationship

Deletes relationships between nodes.

Workflow:

graph_name → resolve source node → resolve target node → relationship type → confirmation → delete relationship

---

# Inspection Tools

Located in:

graphInspectionOrchestration/inspectionOrchestrationTools.py

These tools inspect the graph without modifying it.

## graph_nodes_count

Returns the total number of nodes and relationships.

Example output:

{
  "node_count": 120,
  "relationship_count": 310
}

---

## count_nodes_by_label

Counts nodes belonging to a specific label.

Workflow:

graph_name → node_label → count nodes

Example output:

{
  "node_label": "Person",
  "node_count": 42
}

---

## count_relationships_by_type

Counts relationships of a specific type.

Workflow:

graph_name → relationship_type → count relationships

Example output:

{
  "relationship_type": "ACTED_IN",
  "relationship_count": 120
}

---

# Finite State Machine (FSM)

Each orchestration tool is implemented as a **Finite State Machine**.

Example workflow:

ASK_GRAPH_NAME  
↓  
ASK_PROPERTY_KEY  
↓  
ASK_PROPERTY_VALUE  
↓  
RESOLVE_NODE  
↓  
USER_CONFIRMATION  
↓  
EXECUTE_OPERATION  

This ensures:

- Safe execution
- Controlled user interaction
- Clear step transitions
- Robust error handling

---

# Validation Layer

Validation is handled through:

validationHelperFxns.py

Examples of validation:

- Graph name validation
- Node label validation
- Relationship type validation
- Property key validation

This prevents:

- Cypher injection
- Invalid schema operations
- Malformed queries

---

# MCP Tool Registration

Tools are dynamically registered with FastMCP.

Example pattern:

available_tools = [
    name for name, _ in inspect.getmembers(ClassName, predicate=inspect.isfunction)
]

Each tool becomes available to the agent automatically.

---

# Example Usage

User prompt:

"Create a relationship between Akash and Kushal"

Agent workflow:

1. Resolve source node  
2. Resolve target node  
3. Ask relationship type  
4. Confirm action  
5. Execute Cypher query  

---

# Design Principles

GraphAgent is built with:

- Modular architecture
- Finite State Machine orchestration
- Clean Neo4j query abstraction
- LLM compatible tool interfaces
- Safe graph mutation workflows

---

# Future Improvements

Potential extensions:

- Graph schema summarization
- Path search tools
- Graph traversal tools
- Graph analytics tools
- Graph embeddings
- Visualization integrations

---

# Author

GraphAgent is designed as a framework for building **graph-aware AI agents using Neo4j**.
