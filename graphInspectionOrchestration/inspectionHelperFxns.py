
from typing import Any, Dict, List
from graphMutationOchestration.validationHelperFxns import ValidationHelperFxns
from neo4jAdpater import Neo4jAdapter


class InspectionHelperFxns:

    def __init__(self, neo4j_adapter: Neo4jAdapter, validation_helper_fxns: ValidationHelperFxns):
        if neo4j_adapter is None:
            raise ValueError("neo4j_adapter is required")
        if validation_helper_fxns is None:
            raise ValueError("validation_helper_fxns is required")

        self.neo4j_adapter = neo4j_adapter
        self.validation_helper_fxns = validation_helper_fxns

    def get_available_graphs(self) -> List[str]:
        try:
            query = """
            SHOW DATABASES
            YIELD name
            RETURN collect(name) AS graph_names
            """
            result = self.neo4j_adapter.run_query(query)
            return result[0]["graph_names"] if result else []
        except Exception as e:
            raise RuntimeError(f"Failed to fetch available graphs: {str(e)}")

    def get_graph_counts(self, graph_name: str) -> Dict[str, Any]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)

            query = f"""
            USE {graph_name}
            MATCH (n)
            WITH count(n) AS node_count
            MATCH ()-[r]->()
            RETURN node_count, count(r) AS relationship_count
            """
            result = self.neo4j_adapter.run_query(query)

            return result[0] if result else {
                "node_count": 0,
                "relationship_count": 0
            }

        except Exception as e:
            raise RuntimeError(f"Failed to fetch graph counts: {str(e)}")

    def get_available_labels(self, graph_name: str) -> List[str]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)

            query = f"""
            USE {graph_name}
            CALL db.labels() YIELD label
            RETURN collect(label) AS labels
            """
            result = self.neo4j_adapter.run_query(query)
            return result[0]["labels"] if result else []

        except Exception as e:
            raise RuntimeError(f"Failed to fetch available labels: {str(e)}")

    def count_nodes_by_label(self, graph_name: str, node_label: str) -> Dict[str, Any]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            self.validation_helper_fxns.validate_label(node_label)

            query = f"""
            USE {graph_name}
            MATCH (n:{node_label})
            RETURN count(n) AS node_count
            """
            result = self.neo4j_adapter.run_query(query)

            return {
                "node_label": node_label,
                "node_count": result[0]["node_count"] if result else 0
            }

        except Exception as e:
            raise RuntimeError(f"Failed to count nodes by label: {str(e)}")

    def get_available_relationship_types(self, graph_name: str) -> List[str]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)

            query = f"""
            USE {graph_name}
            CALL db.relationshipTypes() YIELD relationshipType
            RETURN collect(relationshipType) AS relationship_types
            """
            result = self.neo4j_adapter.run_query(query)
            return result[0]["relationship_types"] if result else []

        except Exception as e:
            raise RuntimeError(f"Failed to fetch relationship types: {str(e)}")

    def count_relationships_by_type(self, graph_name: str, relationship_type: str) -> Dict[str, Any]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            self.validation_helper_fxns.validate_relationship_type(relationship_type)

            query = f"""
            USE {graph_name}
            MATCH ()-[r:{relationship_type}]->()
            RETURN count(r) AS relationship_count
            """
            result = self.neo4j_adapter.run_query(query)

            return {
                "relationship_type": relationship_type,
                "relationship_count": result[0]["relationship_count"] if result else 0
            }

        except Exception as e:
            raise RuntimeError(f"Failed to count relationships by type: {str(e)}")