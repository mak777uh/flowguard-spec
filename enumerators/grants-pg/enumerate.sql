-- Enumerator: which database objects can write a given table, and where the declared control point is.
--
-- Output columns (uniform across all queries):
--   item_kind     path | control_point
--   kind          privilege | function | disabled_control | view_trigger | dynamic_sql | trigger_chain
--   entry         stable-ish identifier of the writer
--   control_point empty when the writer does not pass through one
--   detail        privilege type, definer flag, trigger state
--   confidence    catalog | text_search   (how the row was established)
--
-- The database and table are substituted by the driver: :schema and :table.
-- Every query is a pure catalogue read. Nothing here needs superuser.

SELECT 'path' AS item_kind, 'privilege' AS kind,
       format('role:%s table:%s.%s', g.grantee, g.table_schema, g.table_name) AS entry,
       '' AS control_point, g.privilege_type AS detail, 'catalog' AS confidence
FROM information_schema.role_table_grants g
WHERE g.table_schema = :'schema' AND g.table_name = :'table'
  AND g.grantee NOT IN ('postgres', 'PUBLIC')
  AND g.privilege_type IN ('INSERT', 'UPDATE', 'DELETE', 'TRUNCATE')

UNION ALL
SELECT 'path', 'function',
       format('function:%s.%s', n.nspname, p.proname),
       -- Empty on purpose: a writer is not a control point just because it is a function. The
       -- control point is reported separately (item_kind = 'control_point'). Setting this to the
       -- function itself made every writer claim to be its own control point (E-M26).
       '',
       CASE WHEN p.prosecdef THEN 'SECURITY DEFINER' ELSE 'SECURITY INVOKER' END,
       'catalog'
FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = :'schema'
  AND p.prokind IN ('f', 'p')
  AND p.prosrc ~* ('(update|insert[[:space:]]+into|delete[[:space:]]+from)[^;]{0,200}' || :'table')
  -- Exclude the declared control point BY IDENTITY, not by name: with an overload present the name
  -- matches two different functions, and dropping both hides the one that writes the table directly
  -- (E-M25). When the name is ambiguous, keep every candidate and let the merger report it.
  AND NOT (
        p.proname = 'transfer'
        AND (SELECT count(*)
             FROM pg_proc p2 JOIN pg_namespace n2 ON n2.oid = p2.pronamespace
             WHERE n2.nspname = :'schema' AND p2.proname = 'transfer') = 1
      )

UNION ALL
SELECT 'path', 'disabled_control',
       format('trigger:%s on %s', t.tgname, c.relname),
       '', 'tgenabled=' || t.tgenabled::text, 'catalog'
FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = :'schema' AND c.relname = :'table'
  AND NOT t.tgisinternal AND t.tgenabled <> 'O'

UNION ALL
SELECT 'path', 'view_trigger',
       format('view:%s trigger:%s', c.relname, t.tgname),
       '', 'INSTEAD OF', 'catalog'
FROM pg_trigger t
JOIN pg_class c ON c.oid = t.tgrelid
JOIN pg_proc p ON p.oid = t.tgfoid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = :'schema' AND c.relkind = 'v'
  AND p.prosrc ~* ('(update|insert[[:space:]]+into|delete[[:space:]]+from)[^;]{0,200}' || :'table')

UNION ALL
SELECT 'path', 'dynamic_sql',
       format('function:%s.%s', n.nspname, p.proname),
       '', 'EXECUTE with the table name assembled at runtime', 'text_search'
FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = :'schema'
  AND p.prosrc ILIKE '%execute%'
  AND p.prosrc ILIKE '%' || :'table' || '%'

UNION ALL
SELECT 'path', 'trigger_chain',
       format('table:%s trigger:%s', c.relname, t.tgname),
       '', 'writes ' || :'table' || ' from another table', 'text_search'
FROM pg_trigger t
JOIN pg_class c ON c.oid = t.tgrelid
JOIN pg_proc p ON p.oid = t.tgfoid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = :'schema' AND c.relname <> :'table' AND c.relkind <> 'v'
  AND NOT t.tgisinternal
  AND p.prosrc ~* ('(update|insert[[:space:]]+into|delete[[:space:]]+from)[^;]{0,200}' || :'table')

UNION ALL
SELECT 'control_point', 'function',
       format('function:%s.%s', n.nspname, p.proname),
       format('function:%s.%s', n.nspname, p.proname), 'declared by the caller', 'catalog'
FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = :'schema' AND p.proname = 'transfer'

UNION ALL
-- A foreign key whose CHILD is the target, with a cascading action, is a write path into the
-- target that no grant or function mentions: deleting the parent row deletes or rewrites target
-- rows. GitLab has two such keys into `projects` (namespaces, organizations), and the enumerator
-- missed both until an independent oracle pointed at them (E-M41).
SELECT 'path', 'fk_cascade',
       format('fk:%s -> %s', parent.relname, child.relname),
       '',
       'ON DELETE ' || CASE con.confdeltype WHEN 'c' THEN 'CASCADE'
                                          WHEN 'n' THEN 'SET NULL'
                                          WHEN 'd' THEN 'SET DEFAULT'
                                          ELSE con.confdeltype::text END
         || CASE WHEN con.confupdtype IN ('c','n','d') THEN ', ON UPDATE cascades' ELSE '' END,
       'catalog'
FROM pg_constraint con
JOIN pg_class child ON child.oid = con.conrelid
JOIN pg_class parent ON parent.oid = con.confrelid
JOIN pg_namespace n ON n.oid = child.relnamespace
WHERE con.contype = 'f'
  AND n.nspname = :'schema'
  AND child.relname = :'table'
  AND (con.confdeltype IN ('c','n','d') OR con.confupdtype IN ('c','n','d'))

ORDER BY 2, 3;
