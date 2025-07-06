/* Document nodes */
CREATE CONSTRAINT doc_id_unique IF NOT EXISTS
FOR (d:Document)
REQUIRE d.id IS UNIQUE;

/* Entity nodes */
CREATE CONSTRAINT entity_name_unique IF NOT EXISTS
FOR (e:Entity)
REQUIRE e.name IS UNIQUE;

/* Optional indexes for fast lookup */
CREATE INDEX entity_name_index IF NOT EXISTS
FOR (e:Entity)
ON (e.name);
