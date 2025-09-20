# Dict2Cypher

Convert Python dicts into Neo4j Cypher queries **easily and safely**.  

This library allows you to build Cypher queries from Python dictionaries and lists without ever executing them. Perfect for generating, testing, and templating Neo4j queries.

## Features

- Create, Merge, Delete nodes and relationships
- Match complex paths
- Bulk operations
- Traversals with depth
- WHERE and filters as strings
- Auto-generated or custom aliases
- Indexes and constraints generation
- Only string output, **no Neo4j execution**

## Installation

```bash
pip install dict2cypher
```

## Usage

```python3
from dict2cypher import Dict2Cypher

# Simple MATCH
q = Dict2Cypher.match({"Person#p": {"name": "Alice"}}).return_("p")
print(q.cypher())
# MATCH (p:Person {name: 'Alice'}) RETURN p

# Create Node + Relationship
nodes = [{"Person#p": {"name": "Alice"}}, {"Person#q": {"name": "Bob"}}]
rel = {"KNOWS#k": {"from": "p", "to": "q", "since": 2020}}
q = Dict2Cypher.create(nodes + [rel])
print(q.cypher())
# CREATE (p:Person {name: 'Alice'})
# CREATE (q:Person {name: 'Bob'})
# CREATE (p)-[k:KNOWS {since: 2020}]->(q)
```

## Why Use Dict2Cypher?

- Generates Cypher queries safely from Python structures
- Works with complex paths, relationships, and filters
- Useful for testing, templating, or building query builders
- Keeps your logic in Python, Cypher as pure output
