# Dict2Cypher.py
import itertools

class Dict2Cypher:
    _alias_counter = itertools.count()

    @classmethod
    def _gen_alias(cls, base="p"):
        return f"{base}{next(cls._alias_counter)}"

    @classmethod
    def match(cls, paths):
        return Query("MATCH", paths)

    @classmethod
    def create(cls, paths):
        return Query("CREATE", paths)

    @classmethod
    def merge(cls, paths):
        return Query("MERGE", paths)

    @classmethod
    def delete(cls, paths, detach=False):
        return Query("DELETE", paths, detach=detach)

    @classmethod
    def traverse(cls, start_alias, rel_type, depth=1, direction="OUT"):
        path = f"({start_alias})-[:{rel_type}*1..{depth}]->(x)"
        return Query("MATCH", path)

    @classmethod
    def create_index(cls, label, prop, unique=False):
        q = f"CREATE {'CONSTRAINT' if unique else 'INDEX'} FOR (n:{label})"
        if unique:
            q += f" REQUIRE n.{prop} IS UNIQUE"
        else:
            q += f" ON (n.{prop})"
        return QueryRaw(q)

    @classmethod
    def create_constraint(cls, label, prop, type="UNIQUE"):
        q = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{prop} IS {type}"
        return QueryRaw(q)

    @classmethod
    def match_node(cls, label, alias=None, props=None):
        alias = alias or cls._gen_alias()
        return cls.match({f"{label}#{alias}": props or {}})

    @classmethod
    def create_node(cls, label, alias=None, props=None):
        alias = alias or cls._gen_alias()
        return cls.create({f"{label}#{alias}": props or {}})

    @classmethod
    def merge_node(cls, label, alias=None, props=None):
        alias = alias or cls._gen_alias()
        return cls.merge({f"{label}#{alias}": props or {}})

    @classmethod
    def create_rel(cls, from_alias, to_alias, rel_type, alias=None, props=None):
        alias = alias or cls._gen_alias()
        return cls.create({f"{rel_type}#{alias}": {"from": from_alias, "to": to_alias, **(props or {})}})

    @classmethod
    def match_rel(cls, from_alias, to_alias, rel_type, alias=None):
        alias = alias or cls._gen_alias()
        return cls.match({f"{rel_type}#{alias}": {"from": from_alias, "to": to_alias}})

class Query:
    def __init__(self, action, paths, detach=False):
        self.action = action
        self.paths = paths if isinstance(paths, list) else [paths]
        self.detach = detach
        self._where = None
        self._set = None
        self._return = None

    def where(self, condition):
        self._where = condition
        return self

    def set(self, props):
        self._set = props
        return self

    def return_(self, *args):
        self._return = args
        return self

    def cypher(self):
        if self.action == "DELETE":
            parts = [self._delete_cypher()]
        else:
            parts = [self._format_path(p, self.action) for p in self.paths]

        if self._where:
            parts.append(f"WHERE {self._where}")
        if self._set:
            set_str = ", ".join(f"{k} = {self._format_value(v)}" for k, v in self._set.items())
            parts.append(f"SET {set_str}")
        if self._return:
            parts.append(f"RETURN {','.join(self._return)}")
        return "\n".join(parts)

    def _delete_cypher(self):
        cy = []
        aliases = []
        for p in self.paths:
            cy.append(self._format_path(p, "MATCH"))
            aliases.extend(self._extract_aliases(p))
        if self.detach:
            cy.append(f"DETACH DELETE {','.join(aliases)}")
        else:
            cy.append(f"DELETE {','.join(aliases)}")
        return "\n".join(cy)

    def _extract_aliases(self, p):
        aliases = []
        if isinstance(p, dict):
            for k in p.keys():
                if "#" in k:
                    _, alias = k.split("#")
                else:
                    alias = Dict2Cypher._gen_alias()
                aliases.append(alias)
        elif isinstance(p, str):
            # Already formatted path string with explicit aliases
            aliases.append(p)
        return aliases

    def _format_path(self, p, action):
        if isinstance(p, str):
            return f"{action} {p}"
        elif isinstance(p, dict):
            s = []
            for k, v in p.items():
                alias = None
                if "#" in k:
                    label, alias = k.split("#")
                else:
                    label, alias = k, Dict2Cypher._gen_alias()

                # Relationship with from/to
                if isinstance(v, dict) and "from" in v and "to" in v:
                    start = v["from"]
                    end = v["to"]
                    prop_str = ", ".join(f"{kk}: {self._format_value(vv)}" for kk,vv in v.items() if kk not in ["from","to"])
                    if prop_str:
                        prop_str = " {" + prop_str + "}"
                    s.append(f"({start})-[{alias}:{label}{prop_str}]->({end})")
                else:
                    prop_str = ""
                    if isinstance(v, dict) and v:
                        prop_str = " {" + ", ".join(f"{kk}: {self._format_value(vv)}" for kk,vv in v.items()) + "}"
                    s.append(f"({alias}:{label}{prop_str})")
            return f"{action} " + ", ".join(s)
        return str(p)

    def _format_value(self, v):
        if isinstance(v, str):
            return f"'{v}'"
        elif isinstance(v, bool):
            return "true" if v else "false"
        elif v is None:
            return "null"
        return str(v)


class QueryRaw:
    def __init__(self, cypher):
        self._cypher = cypher

    def cypher(self):
        return self._cypher

class D2C:
    """Höhere Abstraktion für Nodes & Relationships in Neo4j"""

    @staticmethod
    def node(label, alias=None, props=None):
        return Dict2Cypher.create_node(label, alias, props)

    @staticmethod
    def match_node(label, alias=None, props=None):
        return Dict2Cypher.match_node(label, alias, props)

    @staticmethod
    def merge_node(label, alias=None, props=None):
        return Dict2Cypher.merge_node(label, alias, props)

    @staticmethod
    def rel(from_node, to_node, rel_type, alias=None, props=None, action="create"):
        if action.lower() == "create":
            return Dict2Cypher.create_rel(from_node, to_node, rel_type, alias, props)
        elif action.lower() == "match":
            return Dict2Cypher.match_rel(from_node, to_node, rel_type, alias)
        else:
            raise ValueError(f"Unknown action {action}")

    @staticmethod
    def chain(*elements, return_aliases=None):
        """
        Baut mehrere Nodes & Relationships zusammen, fügt automatisch RETURN hinzu.
        Beispiel:
        chain(
            D2C.node("Person", "p", {"name":"Alice"}),
            D2C.node("Person", "q", {"name":"Bob"}),
            D2C.rel("p","q","KNOWS", "k")
        )
        """
        cy_parts = [e.cypher() for e in elements]
        if return_aliases:
            cy_parts.append("RETURN " + ",".join(return_aliases))
        return "\n".join(cy_parts)

    @staticmethod
    def auto_chain(elements):
        """
        Automatisches RETURN für alle Aliase in Nodes & Relationships.
        Nutzt interne Alias-Erkennung.
        """
        aliases = []
        for e in elements:
            if isinstance(e, Query):
                for p in e.paths:
                    if isinstance(p, dict):
                        aliases.extend(e._extract_aliases(p))
        return D2C.chain(*elements, return_aliases=aliases)
