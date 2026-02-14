from typing import Any, Dict
from neo4j import GraphDatabase

class Neo4jAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.driver = GraphDatabase.driver(config["URI"], auth=(config["USERNAME"], config["PASSWORD"]))

    def close(self):
        self.driver.close()

    def verify_connection(self):
        try:
            with self.driver.session():
                self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]