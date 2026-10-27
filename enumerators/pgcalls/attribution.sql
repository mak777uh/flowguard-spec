-- Call-graph enumerator: which PL/pgSQL functions reach the declared control point?
--
-- It does not find paths (that is the grants enumerator's job). It contributes *attribution*:
-- for each function in the schema, does its body call the control point, directly or transitively?
--
-- Output columns: entry | attributed_to | method | confidence
--   entry         function:<schema>.<name>
--   attributed_to the declared control point, or empty when the function never reaches it
--   method        direct | transitive
--   confidence    catalog (call text parsed from prosrc)
--
-- Blind spots are declared in the README, not here, and they are real: dynamic SQL, calls
-- through variables, EXECUTE, C functions, and anything outside PL/pgSQL are invisible.

WITH RECURSIVE edges AS (
  -- every function body, and the inner calls it mentions that resolve to a function in the schema
  SELECT p.oid AS caller, p.proname AS caller_name,
         q.proname AS callee_name
  FROM pg_proc p
  JOIN pg_namespace n ON n.oid = p.pronamespace
  JOIN pg_namespace nq ON true
  JOIN pg_proc q ON q.pronamespace = nq.oid
  WHERE n.nspname = :'schema'
    AND p.prokind IN ('f', 'p')
    AND q.prokind IN ('f', 'p')
    -- the call appears in the body, qualified or bare, followed by an opening parenthesis
    AND p.prosrc ~* ('(^|[^a-zA-Z0-9_])(' || nq.nspname || '\.)?' || q.proname || '[[:space:]]*\(')
    AND p.oid <> q.oid
),
direct AS (
  SELECT DISTINCT caller, caller_name FROM edges WHERE callee_name = :'control'
),
closure AS (
  SELECT caller, caller_name, 1 AS depth, 'direct' AS method FROM direct
  UNION
  SELECT e.caller, e.caller_name, c.depth + 1, 'transitive'
  FROM edges e JOIN closure c ON e.callee_name = c.caller_name
  WHERE c.depth < 8
),
best AS (
  SELECT caller_name, MIN(depth) AS depth,
         MIN(method) AS method   -- 'direct' sorts before 'transitive'
  FROM closure GROUP BY caller_name
)
SELECT format('function:%s.%s', :'schema', p.proname) AS entry,
       format('function:%s.%s', :'schema', :'control') AS attributed_to,
       b.method,
       'catalog' AS confidence
FROM best b JOIN pg_proc p ON p.proname = b.caller_name
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = :'schema'
ORDER BY entry;
