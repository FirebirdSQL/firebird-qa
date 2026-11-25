#coding:utf-8

"""
ID:          issue-9157
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9157
TITLE:       Improvement: Rewrite hash join hash table for better scalability
DESCRIPTION:
    Commit 86daeaf3d74c5b207a3562c853cb1c0148e8eacd ("Rewrite hash join hash table for
    better scalability") re-implemented HashJoin::HashTable: instead of the fixed
    HASH_SIZE = 1009 bucket table with per-bucket CollisionList objects, it now collects
    {hash, position} pairs into a flat array and, once the inner streams are fully read,
    groups them by bucket in a single counting-sort pass. The table size is derived from
    the ACTUAL number of entries (per stream), so long collision chains on large inner
    streams are gone and lookups are binary searches inside short, contiguous, sorted
    bucket ranges.

    Important side effect of this commit: HashJoin::maxCapacity() was raised from
        HASH_SIZE * 1000       = 1009    * 1000 =   1009000   (old)
        MAX_HASH_SIZE * 4      = 1000003 * 4    =   4000012   (new)
    The optimizer consults this limit in two places:
    - Optimizer.cpp, Optimizer::generateEquiJoin(): if the 2nd-largest river cardinality
      ('maxCardinality2') exceeds maxCapacity(), an INNER equi-join is compiled as MERGE
      join ('hashOverflow'), otherwise as HASH join;
    - InnerJoin.cpp, when a stream is considered to be hash-joined to the prior ones.

    THIS IS WHAT THE TEST CHECKS, and it works within ONE instance only (the QA plugin
    can not run two FB snapshots at once, and this commit adds no new mon$ counters or
    columns that could be used to detect it in MON$ tables):

    Two tables with 1100000 rows each are created. Since
        1009000  <  1100000  <=  4000012,
    the equi-join of these tables must be compiled as HASH join on builds that contain
    the commit, and as MERGE join on pre-commit builds (test fails there - by design,
    this is how the presence of the feature is detected). Both the plain-table join
    (query #1000) and the derived-tables join (query #2000) are checked: the latter
    forces rivers to be formed separately, exercising Optimizer::generateEquiJoin()
    directly. Small-tables join (query #3000) is a control case: its cardinality is
    below the OLD maxCapacity() too, so HASH join must be chosen on ALL builds - this
    proves that the MERGE-vs-HASH flip above is threshold-driven rather than absence
    of the hash join method itself.

    Elapsed times are NOT asserted either: the requirement for this test is to
    illustrate the effect of the commit without comparing performance of two
    different FB snapshots.
NOTES:
    [25.11.2026] pzotov
    Reduced to PLAN-only checks: no statement is executed now, statements are only
    prepared and their plans are verified.
    Source analysis:
        src/jrd/recsrc/HashJoin.cpp (line with 'hashOverflow'),
        src/jrd/optimizer/InnerJoin.cpp (line with 'hashCardinality <= maxCapacity()').

    Confirmed previous plan (with MERGE join) on 6.0.0.2446-0b6d977.
    Checked on 6.0.0.2447-77d8185, 6.0.0.2507-b5665a1: all queries use HASH join.
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()

act = python_act('db')

tmp_sql = temp_file('gh_9157.tmp.sql')

ddl_and_dml_script = """
    recreate table big1(id int, k int, nk int);
    recreate table big2(id int, k int, nk int);
    recreate table small1(id int primary key, k int);
    recreate table small2(id int primary key, k int);

    insert into big1(id, k, nk) select i, mod(i, 12345), mod(i, 78965)
    from generate_series(1,1100000) as s(i)
    ;

    insert into big2(id, k, nk) select i, mod(i, 54321), mod(i, 56789)
    from generate_series(1,1100000) as s(i)
    ;

    insert into small1(id, k) select i, mod(i, 100) from generate_series(1,1000) as s(i);
    insert into small2(id, k) select i, mod(i, 100) from generate_series(1,1000) as s(i);
    commit;
"""

# key -> (sql, description)
qry_map = {
    1000:
    (
        "select count(*) from big1 a join big2 b on a.id = b.id"
        ,'plain-table INNER equi-join on UNIQUE key, 2 x 2000000 rows: 1_009_000 < 2_000_000 <= 4_000_012,'
        ,'thus pre-commit builds compile it as MERGE join, post-commit as HASH join'
    )
    ,2000:
    (
        """
        select count(*)
        from (select id from big1) p
        join (select id from big2) q on p.id = q.id
        """
        ,'derived-tables INNER equi-join on UNIQUE key, 2 x 2000000 rows: same threshold as above,'
        ,'but now both streams form separate rivers => Optimizer::generateEquiJoin() decides HASH vs MERGE'
    )
    ,3000:
    (
        """
        select count(*)
        from (select k from small1) p
        join (select k from small2) q on p.k = q.k
        """
        ,'CONTROL: join of small tables (1000 rows each, 100 distinct keys); cardinality is far below'
        ,'the OLD maxCapacity() too, so HASH join must be used on ALL builds (pre-commit ones as well)'
    )
}

expected_plans = {
    1000: 'PLAN HASH ("A" NATURAL, "B" NATURAL)'
    ,2000: 'PLAN HASH ("P" "PUBLIC"."BIG1" NATURAL, "Q" "PUBLIC"."BIG2" NATURAL)'
    ,3000: 'PLAN HASH ("P" "PUBLIC"."SMALL1" NATURAL, "Q" "PUBLIC"."SMALL2" NATURAL)'
}

@pytest.mark.ai
@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, capsys):

    tmp_sql.write_text(ddl_and_dml_script, encoding = 'utf8')

    act.isql(switches = ['-q'], charset = 'utf8', input_file = tmp_sql, combine_output = True)
    assert act.return_code == 0, 'Data generation failed, see output: ' + act.clean_stdout
    act.reset()

    with act.db.connect() as con:
        cur = con.cursor()

        for q_idx, q_tuple in qry_map.items():
            test_sql = q_tuple[0]
            qry_comments = q_tuple[1:3]

            print(q_idx)
            print(test_sql.strip())
            for c in qry_comments:
                print(c)

            # Statements are only prepared, never executed: the plan is what
            # this test verifies, actual join processing would only waste time.
            ps = cur.prepare(test_sql)
            plan = ps.plan
            print(plan)

            assert 'HASH' in plan and 'MERGE' not in plan, \
                f'Query {q_idx}: HASH join was not used, plan: {plan}'
            ps.free()

    act.expected_stdout = f"""
        1000
        {qry_map[1000][0]}
        {qry_map[1000][1]}
        {qry_map[1000][2]}
        {expected_plans[1000]}
        2000
        {qry_map[2000][0].strip()}
        {qry_map[2000][1]}
        {qry_map[2000][2]}
        {expected_plans[2000]}
        3000
        {qry_map[3000][0].strip()}
        {qry_map[3000][1]}
        {qry_map[3000][2]}
        {expected_plans[3000]}
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
