# graphMutationOchestration/validationHelperFxns.py

import re

from neo4jAdpater import Neo4jAdapter


class ValidationHelperFxns:

    def __init__(self, neo4j_adapter: Neo4jAdapter):
        if neo4j_adapter is None:
            raise ValueError("neo4j_adapter is required")
        self.neo4j_adapter = neo4j_adapter

    @staticmethod
    def is_valid_identifier(value: str) -> bool:
        if value is None or not isinstance(value, str):
            return False
        value = value.strip()
        if value == "":
            return False
        return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", value))

    def validate_graph_name(self, graph_name: str) -> None:
        if graph_name is None:
            raise ValueError("Graph name cannot be None.")
        if not isinstance(graph_name, str):
            raise ValueError("Graph name must be a string.")

        graph_name = graph_name.strip()
        if graph_name == "":
            raise ValueError("Graph name cannot be empty.")

        if not self.is_valid_identifier(graph_name):
            raise ValueError(
                f"Invalid graph name '{graph_name}'. "
                "Graph names must start with a letter or underscore and contain only letters, numbers, or underscores."
            )

    def validate_label(self, label: str) -> None:
        if label is None:
            raise ValueError("Label cannot be None.")
        if not isinstance(label, str):
            raise ValueError("Label must be a string.")

        label = label.strip()
        if label == "":
            raise ValueError("Label cannot be empty.")

        if not self.is_valid_identifier(label):
            raise ValueError(
                f"Invalid label '{label}'. "
                "Labels must start with a letter or underscore and contain only letters, numbers, or underscores."
            )

    def validate_relationship_type(self, relationship_type: str) -> None:
        if relationship_type is None:
            raise ValueError("Relationship type cannot be None.")
        if not isinstance(relationship_type, str):
            raise ValueError("Relationship type must be a string.")

        relationship_type = relationship_type.strip()
        if relationship_type == "":
            raise ValueError("Relationship type cannot be empty.")

        if not self.is_valid_identifier(relationship_type):
            raise ValueError(
                f"Invalid relationship type '{relationship_type}'. "
                "Relationship types must start with a letter or underscore and contain only letters, numbers, or underscores."
            )

    def validate_property_name(self, property_key: str) -> None:
        if property_key is None:
            raise ValueError("Property name cannot be None.")
        if not isinstance(property_key, str):
            raise ValueError("Property name must be a string.")

        property_key = property_key.strip()
        if property_key == "":
            raise ValueError("Property name cannot be empty.")

        if not self.is_valid_identifier(property_key):
            raise ValueError(
                f"Invalid property name '{property_key}'. "
                "Property names must start with a letter or underscore and contain only letters, numbers, or underscores."
            )

    def format_labels(self, labels: list[str]) -> str:
        if labels is None or not isinstance(labels, list) or len(labels) == 0:
            raise ValueError("Labels must be a non-empty list.")

        cleaned_labels = []
        for label in labels:
            self.validate_label(label)
            cleaned_labels.append(label.strip())

        return ":".join(cleaned_labels)