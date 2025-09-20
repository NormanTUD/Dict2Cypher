import unittest
from Dict2Cypher import Dict2Cypher

class TestDict2Cypher(unittest.TestCase):

    def test_simple_match_node(self):
        q = Dict2Cypher.match({"Person#p": {"name": "Alice"}}).return_("p")
        self.assertIn("MATCH", q.cypher())
        self.assertIn("RETURN p", q.cypher())
        self.assertIn("Alice", q.cypher())

    def test_auto_alias_node(self):
        q = Dict2Cypher.match({"Person": {"name": "Bob"}}).return_("p0")
        cy = q.cypher()
        self.assertIn("(p0:Person", cy)
        self.assertIn("Bob", cy)

    def test_create_node_and_relationship(self):
        nodes = [{"Person#p": {"name": "Alice"}}, {"Person#q": {"name": "Bob"}}]
        rel = {"KNOWS#k": {"from": "p", "to": "q", "since": 2020}}
        q = Dict2Cypher.create(nodes + [rel])
        cy = q.cypher()
        self.assertIn("CREATE (p:Person", cy)
        self.assertIn("CREATE (q:Person", cy)
        self.assertIn("CREATE (p)-[k:KNOWS", cy)
        self.assertIn("since: 2020", cy)

    def test_delete_node_with_detach(self):
        q = Dict2Cypher.delete({"Person#p": {"name": "Alice"}}, detach=True)
        cy = q.cypher()
        self.assertIn("DETACH DELETE", cy)
        self.assertIn("MATCH (p:Person", cy)

    def test_where_string_filter(self):
        q = Dict2Cypher.match({"Person#p": {}}).where("_.age > 30 AND NOT _.name='Bob'").return_("p")
        cy = q.cypher()
        self.assertIn("WHERE _.age > 30 AND NOT _.name='Bob'", cy)

    def test_bulk_update_set(self):
        q = Dict2Cypher.match({"Person#p": {"city": "Berlin"}}).set({"p.age": 30})
        cy = q.cypher()
        self.assertIn("SET p.age = 30", cy)

    def test_traverse_depth(self):
        q = Dict2Cypher.traverse("p", "KNOWS", depth=3).return_("x.name")
        cy = q.cypher()
        self.assertIn("[:KNOWS*1..3]", cy)
        self.assertIn("RETURN x.name", cy)

    def test_index_and_constraint(self):
        idx = Dict2Cypher.create_index("Person", "email", unique=True)
        self.assertIn("CREATE CONSTRAINT", idx.cypher())
        c = Dict2Cypher.create_constraint("Person", "email", type="UNIQUE")
        self.assertIn("IS UNIQUE", c.cypher())

    def test_multiple_paths(self):
        paths = [
            {"Person#p": {"name": "Alice"}},
            {"Person#q": {"name": "Bob"}},
            {"KNOWS#k": {"from": "p", "to": "q"}}
        ]
        q = Dict2Cypher.match(paths).return_("p,q")
        cy = q.cypher()
        self.assertIn("MATCH", cy)
        self.assertIn("(p:Person", cy)
        self.assertIn("(q:Person", cy)
        self.assertIn("RETURN p,q", cy)

    def test_edge_case_empty_props(self):
        q = Dict2Cypher.create([{"Person#p": {}}])
        cy = q.cypher()
        self.assertIn("(p:Person)", cy)

    def test_edge_case_reserved_keywords(self):
        q = Dict2Cypher.create([{"Match#m": {"type": "Special"}}])
        cy = q.cypher()
        self.assertIn("(m:Match", cy)
        self.assertIn("type: 'Special'", cy)

if __name__ == "__main__":
    unittest.main()
