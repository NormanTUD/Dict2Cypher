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
