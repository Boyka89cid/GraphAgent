from typing import Any, Dict, List, Optional
from graphMutationOchestration.validationHelperFxns import ValidationHelperFxns
from neo4jAdpater import Neo4jAdapter

class GraphHelperFxns:

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

    def get_property_keys_for_labels(self, graph_name: str, labels: List[str]) -> List[str]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            labels_string = self.validation_helper_fxns.format_labels(labels)

            query = f"""
            USE {graph_name}
            MATCH (n:{labels_string})
            UNWIND keys(n) AS key
            RETURN collect(DISTINCT key) AS properties
            """
            result = self.neo4j_adapter.run_query(query)
            return result[0]["properties"] if result else []

        except Exception as e:
            raise RuntimeError(f"Failed to fetch property keys for labels: {str(e)}")

    def create_node(
        self,
        graph_name: str,
        labels: List[str],
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            labels_string = self.validation_helper_fxns.format_labels(labels)

            query = f"""
            USE {graph_name}
            CREATE (n:{labels_string} $properties)
            RETURN elementId(n) AS node_id,
                   labels(n) AS labels,
                   properties(n) AS properties
            """
            result = self.neo4j_adapter.run_query(
                query,
                {"properties": properties or {}}
            )
            return result[0] if result else {}

        except Exception as e:
            raise RuntimeError(f"Failed to create node: {str(e)}")

    def get_all_node_property_keys(self, graph_name: str) -> List[str]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)

            query = f"""
            USE {graph_name}
            MATCH (n)
            UNWIND keys(n) AS k
            RETURN collect(DISTINCT k) AS property_keys
            """
            result = self.neo4j_adapter.run_query(query)
            return result[0]["property_keys"] if result else []

        except Exception as e:
            raise RuntimeError(f"Failed to fetch node property keys: {str(e)}")

    def find_nodes_by_property(
        self,
        graph_name: str,
        property_key: str,
        property_value: Any
    ) -> List[Dict[str, Any]]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            self.validation_helper_fxns.validate_property_name(property_key)

            query = f"""
            USE {graph_name}
            MATCH (n)
            WHERE n.{property_key} = $property_value
            RETURN elementId(n) AS node_id,
                   labels(n) AS labels,
                   properties(n) AS properties
            """
            result = self.neo4j_adapter.run_query(
                query,
                {"property_value": property_value}
            )
            return result if result else []

        except Exception as e:
            raise RuntimeError(f"Failed to find nodes by property: {str(e)}")

    def get_node_by_id(self, graph_name: str, node_id: str) -> Optional[Dict[str, Any]]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)

            query = f"""
            USE {graph_name}
            MATCH (n)
            WHERE elementId(n) = $node_id
            RETURN elementId(n) AS node_id,
                   labels(n) AS labels,
                   properties(n) AS properties
            """
            result = self.neo4j_adapter.run_query(query, {"node_id": node_id})
            return result[0] if result else None

        except Exception as e:
            raise RuntimeError(f"Failed to fetch node by id: {str(e)}")

    def preview_node_for_delete(self, graph_name: str, node_id: str) -> Optional[Dict[str, Any]]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)

            query = f"""
            USE {graph_name}
            MATCH (n)
            WHERE elementId(n) = $node_id
            OPTIONAL MATCH (n)-[r]-()
            RETURN elementId(n) AS node_id,
                   labels(n) AS labels,
                   properties(n) AS properties,
                   count(r) AS degree
            """
            result = self.neo4j_adapter.run_query(query, {"node_id": node_id})
            return result[0] if result else None

        except Exception as e:
            raise RuntimeError(f"Failed to preview node for delete: {str(e)}")

    def delete_node_with_confirmation(self, graph_name: str, node_id: str) -> Optional[Dict[str, Any]]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)

            query = f"""
            USE {graph_name}
            MATCH (n)
            WHERE elementId(n) = $node_id
            OPTIONAL MATCH (n)-[r]-()
            WITH n,
                 labels(n) AS labels_before_delete,
                 properties(n) AS properties_before_delete,
                 count(r) AS degree_before_delete
            DETACH DELETE n
            RETURN labels_before_delete, properties_before_delete, degree_before_delete
            """
            result = self.neo4j_adapter.run_query(query, {"node_id": node_id})
            return result[0] if result else None

        except Exception as e:
            raise RuntimeError(f"Failed to delete node: {str(e)}")

    def update_node_properties(
        self,
        graph_name: str,
        node_id: str,
        properties: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)

            query = f"""
            USE {graph_name}
            MATCH (n)
            WHERE elementId(n) = $node_id
            SET n += $properties
            RETURN elementId(n) AS node_id,
                   labels(n) AS labels,
                   properties(n) AS properties
            """
            result = self.neo4j_adapter.run_query(
                query,
                {
                    "node_id": node_id,
                    "properties": properties or {}
                }
            )
            return result[0] if result else None

        except Exception as e:
            raise RuntimeError(f"Failed to update node properties: {str(e)}")

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

    def get_relationship_property_keys(
        self,
        graph_name: str,
        relationship_type: str
    ) -> List[str]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            self.validation_helper_fxns.validate_relationship_type(relationship_type)

            query = f"""
            USE {graph_name}
            MATCH ()-[r:{relationship_type}]->()
            UNWIND keys(r) AS key
            RETURN collect(DISTINCT key) AS properties
            """
            result = self.neo4j_adapter.run_query(query)
            return result[0]["properties"] if result else []

        except Exception as e:
            raise RuntimeError(f"Failed to fetch relationship property keys: {str(e)}")

    def create_relationship(
        self,
        graph_name: str,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            self.validation_helper_fxns.validate_relationship_type(relationship_type)

            query = f"""
            USE {graph_name}
            MATCH (a), (b)
            WHERE elementId(a) = $source_node_id AND elementId(b) = $target_node_id
            CREATE (a)-[r:{relationship_type} $properties]->(b)
            RETURN elementId(r) AS relationship_id,
                   type(r) AS relationship_type,
                   properties(r) AS properties
            """
            result = self.neo4j_adapter.run_query(
                query,
                {
                    "source_node_id": source_node_id,
                    "target_node_id": target_node_id,
                    "properties": properties or {}
                }
            )
            return result[0] if result else None

        except Exception as e:
            raise RuntimeError(f"Failed to create relationship: {str(e)}")

    def preview_relationship_for_delete(
        self,
        graph_name: str,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str
    ) -> Optional[Dict[str, Any]]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            self.validation_helper_fxns.validate_relationship_type(relationship_type)

            query = f"""
            USE {graph_name}
            MATCH (a)-[r:{relationship_type}]->(b)
            WHERE elementId(a) = $source_node_id AND elementId(b) = $target_node_id
            RETURN elementId(r) AS relationship_id,
                   type(r) AS relationship_type,
                   properties(r) AS relationship_properties,
                   elementId(a) AS source_node_id,
                   elementId(b) AS target_node_id
            LIMIT 1
            """
            result = self.neo4j_adapter.run_query(
                query,
                {
                    "source_node_id": source_node_id,
                    "target_node_id": target_node_id
                }
            )
            return result[0] if result else None

        except Exception as e:
            raise RuntimeError(f"Failed to preview relationship for delete: {str(e)}")

    def delete_relationship_with_confirmation(
        self,
        graph_name: str,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str
    ) -> Optional[Dict[str, Any]]:
        try:
            self.validation_helper_fxns.validate_graph_name(graph_name)
            self.validation_helper_fxns.validate_relationship_type(relationship_type)

            query = f"""
            USE {graph_name}
            MATCH (a)-[r:{relationship_type}]->(b)
            WHERE elementId(a) = $source_node_id AND elementId(b) = $target_node_id
            WITH properties(r) AS properties_before_delete,
                 elementId(r) AS relationship_id
            DELETE r
            RETURN relationship_id, properties_before_delete
            """
            result = self.neo4j_adapter.run_query(
                query,
                {
                    "source_node_id": source_node_id,
                    "target_node_id": target_node_id
                }
            )
            return result[0] if result else None

        except Exception as e:
            raise RuntimeError(f"Failed to delete relationship: {str(e)}")