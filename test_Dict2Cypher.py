import unittest
from dict2cypher import Dict2Cypher
import itertools

class TestDict2Cypher(unittest.TestCase):

    def test_simple_match_node(self):
        q = Dict2Cypher.match({"Person#p": {"name": "Alice"}}).return_("p")
        self.assertIn("MATCH", q.cypher())
        self.assertIn("RETURN p", q.cypher())
        self.assertIn("Alice", q.cypher())

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

    def test_none_in_props(self):
        q = Dict2Cypher.create([{"Person#p": {"name": None}}])
        cy = q.cypher()
        self.assertIn("name: null", cy)

    def test_numeric_labels_and_alias(self):
        q = Dict2Cypher.match({"123Label#99": {"value": 42}}).return_("99")
        cy = q.cypher()
        self.assertIn("(99:123Label", cy)
        self.assertIn("42", cy)

    def test_special_chars_in_label_and_alias(self):
        q = Dict2Cypher.create([{"N@me#ali-as": {"x": 1}}])
        cy = q.cypher()
        self.assertIn("(ali-as:N@me", cy)

    def test_nested_relationships_multiple_props(self):
        paths = [{"KNOWS#r": {"from": "a", "to": "b", "since": 2020, "strength": 10}}]
        q = Dict2Cypher.create(paths)
        cy = q.cypher()
        self.assertIn("[r:KNOWS", cy)
        self.assertIn("since: 2020", cy)
        self.assertIn("strength: 10", cy)

    def test_multiple_relationships_same_alias(self):
        paths = [
            {"KNOWS#r": {"from": "a", "to": "b"}},
            {"KNOWS#r": {"from": "b", "to": "c"}}
        ]
        q = Dict2Cypher.create(paths)
        cy = q.cypher()
        self.assertIn("[r:KNOWS", cy)

    def test_empty_string_props(self):
        q = Dict2Cypher.create([{"Person#p": {"name": ""}}])
        cy = q.cypher()
        self.assertIn("name: ''", cy)

    def test_numeric_property_keys(self):
        q = Dict2Cypher.create([{"Person#p": {1: "one"}}])
        cy = q.cypher()
        self.assertIn("1: 'one'", cy)

    def test_alias_generation_for_multiple_nodes(self):
        nodes = [{"Person": {"name": "A"}}, {"Person": {"name": "B"}}]
        q = Dict2Cypher.match(nodes)
        cy = q.cypher()
        self.assertIn("(p0:Person", cy)
        self.assertIn("(p1:Person", cy)

    def test_delete_without_detach(self):
        q = Dict2Cypher.delete({"Person#p": {"name": "X"}})
        cy = q.cypher()
        self.assertIn("DELETE p", cy)
        self.assertNotIn("DETACH", cy)

    def test_traverse_zero_depth(self):
        q = Dict2Cypher.traverse("p", "KNOWS", depth=0)
        cy = q.cypher()
        self.assertIn("*1..0", cy)

    def test_traverse_negative_depth(self):
        q = Dict2Cypher.traverse("p", "KNOWS", depth=-5)
        cy = q.cypher()
        self.assertIn("*1..-5", cy)

    def test_return_multiple_fields(self):
        q = Dict2Cypher.match({"Person#p": {}}).return_("p.name", "p.age")
        cy = q.cypher()
        self.assertIn("RETURN p.name,p.age", cy)

    def test_set_multiple_properties(self):
        q = Dict2Cypher.match({"Person#p": {}}).set({"p.name": "Z", "p.age": 99})
        cy = q.cypher()
        self.assertIn("SET p.name = 'Z', p.age = 99", cy)

    def test_set_empty_properties_dict(self):
        q = Dict2Cypher.match({"Person#p": {}}).set({})
        cy = q.cypher()
        self.assertNotIn("SET", cy)

    def test_create_index_without_unique(self):
        idx = Dict2Cypher.create_index("Person", "name", unique=False)
        cy = idx.cypher()
        self.assertIn("CREATE INDEX", cy)
        self.assertIn("ON (n.name)", cy)

    def test_create_constraint_non_unique_type(self):
        c = Dict2Cypher.create_constraint("Person", "age", type="EXISTS")
        cy = c.cypher()
        self.assertIn("IS EXISTS", cy)

    def test_string_instead_of_dict_path(self):
        q = Dict2Cypher.create("(:Person {name: 'X'})")
        cy = q.cypher()
        self.assertIn("CREATE (:Person", cy)

    def test_multiple_string_paths(self):
        q = Dict2Cypher.match(["(:A)", "(:B)"]).return_("a,b")
        cy = q.cypher()
        self.assertIn("MATCH (:A)", cy)
        self.assertIn("MATCH (:B)", cy)

    def test_edge_case_dot_in_alias(self):
        q = Dict2Cypher.create([{"Person#a.b": {"x": 1}}])
        cy = q.cypher()
        self.assertIn("(a.b:Person", cy)

    def test_unicode_characters_in_props(self):
        q = Dict2Cypher.create([{"Person#p": {"name": "José"}}])
        cy = q.cypher()
        self.assertIn("'José'", cy)

    def test_list_as_property_value(self):
        q = Dict2Cypher.create([{"Person#p": {"tags": [1,2,3]}}])
        cy = q.cypher()
        self.assertIn("[1, 2, 3]", cy)

    def test_dict_as_property_value(self):
        q = Dict2Cypher.create([{"Person#p": {"meta": {"a": 1}}}])
        cy = q.cypher()
        self.assertIn("{'a': 1}", cy)

    def test_duplicate_aliases_generated(self):
        Dict2Cypher._alias_counter = itertools.count(0)
        q = Dict2Cypher.match([{"A": {}}, {"A": {}}])
        cy = q.cypher()
        self.assertIn("(p0:A", cy)
        self.assertIn("(p1:A", cy)

    def test_delete_multiple_nodes(self):
        paths = [{"Person#p": {}}, {"Person#q": {}}]
        q = Dict2Cypher.delete(paths, detach=True)
        cy = q.cypher()
        self.assertIn("DETACH DELETE p,q", cy)

if __name__ == "__main__":
    unittest.main()
