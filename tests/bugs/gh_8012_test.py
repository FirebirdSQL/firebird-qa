#coding:utf-8

"""
ID:          issue-8012
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8012
TITLE:       SELECT crashes the server when an aggregate whose arguments contain a sub-select is used as a GROUP BY item
DESCRIPTION:
    AggNode::dsqlAggregate2Finder() ran a FieldFinder over the arguments of an aggregate in order to
    find out whether that aggregate belongs to the query block being checked. Fields inside a
    sub-select of an argument were counted as well, even when their scope level did not match. For an
    aggregate whose only fields live inside a sub-select, e.g. LIST(DISTINCT (SELECT ...)), this made
    the finder report "no aggregate here", so PASS1_rse() did not reject it as an aggregate in the
    GROUP BY list.
    A DISTINCT aggregate which reaches the GROUP BY list has no sort block: the group item is a
    private copy of the select-list item and is therefore never registered as a map source, hence
    Optimizer::generateAggregateDistincts() does not allocate it, and AggNode::execute() dereferenced
    the null pointer. Aggregates without DISTINCT were simply accepted, although they must be
    rejected as well.
    The same happened for the predicates written inside the arguments: EXISTS, IN, SINGULAR and the
    quantified predicates are RseBoolNode-s, and that class honoured ignoreSubSelects in
    dsqlAggregateFinder() only. Its dsqlFieldFinder() descended into the sub-select of the predicate,
    so a field used there - even a field of the checked block, as the left operand of IN - was taken
    for a field which says something about the scope level of the aggregate.
    Test has four parts:
      1) queries which used to crash the server or to be accepted must now be rejected at compile
         time with "Cannot use an aggregate or window function in a GROUP BY clause" (or, for the
         ones written in a WHERE clause, with "... in a WHERE clause, use HAVING ...");
      2) queries which must stay valid must still return correct data. They cover the cases which
         distinguish "aggregate of the checked block" from "aggregate of a nested block": aggregates
         inside sub-selects, correlated sub-selects which use fields of the outer block (including
         the SQL:2008 rule that allows a set function in a WHERE clause when all aggregated
         arguments are outer references), aggregates in HAVING and in ORDER BY, plain DISTINCT
         aggregates and window functions.
      3) the same checks for the arguments which contain a predicate sub-select instead of a scalar
         one: the four variants of the ticket (IIF(EXISTS(...)), IIF(1 IN (...)), IIF(SINGULAR(...))
         and IIF(100 > ALL (...)) inside a DISTINCT aggregate with GROUP BY 1), the negated and
         combined predicates, the quantified predicates (= ANY, <> ALL, NOT ... = ANY), a predicate
         whose operand is a scalar sub-select, a predicate inside a sub-select, such an aggregate in
         the WHERE clause and in a nested aggregate, in the recursive member of a CTE and as the sort
         item of a hypothetical-set aggregate;
      4) queries of the same shape which are legal and must keep returning the same values: such an
         aggregate in the select list, in HAVING, in ORDER BY and inside a sub-select, a field of the
         checked block as the left operand of IN, an aggregate of a nested block whose argument uses
         fields of the outer block, and a window function with a predicate sub-select in its argument.
NOTES:
    [05.11.2026] AI assistant
        Queries of test_1 are the variants which were used while investigating the ticket.
        Confirmed on 5.0.5.1950 (v5.0-release, without the fix): statements 1, 2, 3, 4 and 7 of
        test_script_1 crashed the server (SIGSEGV in AggNode::execute() with asb == NULL), statement
        5 was accepted without any error, statements 6 and 8 were rejected already before the fix.
        All statements of test_script_2 returned the same values before and after the fix.
        Checked on 5.0.5.1950 with the fix for #8012 applied.
        LIST() returns BLOB SUB_TYPE TEXT here, hence its value is cast to VARCHAR in order to avoid
        printing of blob ids.
    [06.11.2026] AI assistant
        Queries of test_3 and test_4 are the variants which were used while checking the follow-up
        report of the ticket, i.e. the same gap for the predicates inside the arguments.
        Confirmed on the build of commit 61cce64 (the fix of the scalar sub-selects, without the
        override of RseBoolNode::dsqlFieldFinder(), which is what the ticket was re-tested with):
        statements 1, 2, 3, 4 and 10 - 16 of test_script_3 crashed the server (SIGSEGV in
        AggNode::execute() with asb == NULL), statements 5 and 6 were accepted without any error, and
        the remaining statements were rejected already before this part of the fix.
        All statements of test_script_4 returned the same values before and after the fix.
"""

import pytest
from firebird.qa import *

substitutions = [('[ \t]+', ' ')]

db = db_factory()

# Schema and data of the ticket (MELDUNEK / MELDUNEKKART), with names kept.
# Both scripts recreate the tables so that each test can run on its own.
init_isql = """
    recreate table meldunek (id_meldunek integer not null);
    recreate table meldunekkart (id_meldunek integer, id_produktzp integer, ilosc integer);
    delete from meldunek;
    delete from meldunekkart;
    insert into meldunek values (10376);
    insert into meldunek values (10377);
    insert into meldunekkart values (10376, 1, 5);
    insert into meldunekkart values (10376, 2, 7);
    insert into meldunekkart values (10376, null, 9);
    insert into meldunekkart values (10377, 4, 1);
    commit;
    set list on;
    set count off;
"""

# Aggregate of the checked query block, all of whose fields are placed inside a sub-select of its
# arguments. Such an aggregate must be seen by the checks that use Aggregate2Finder.
test_script_1 = init_isql + """
    -- query from the ticket:
    select list(distinct(select sum(MK.ILOSC)
    from MELDUNEKKART MK
    where MK.ID_MELDUNEK = M.ID_MELDUNEK and
    MK.ID_PRODUKTZP is not null), '')
    from MELDUNEK M
    where M.ID_MELDUNEK = 10376
    group by 1;

    select list(distinct (select sum(MK.ILOSC) from MELDUNEKKART MK), '') from MELDUNEK M group by 1;

    select avg(distinct (select max(MK.ILOSC) from MELDUNEKKART MK)) from MELDUNEK M group by 1;

    select count(distinct (select max(MK.ILOSC) from MELDUNEKKART MK)) from MELDUNEK M group by 1;

    -- aggregate without DISTINCT: used to be accepted without an error:
    select sum((select max(MK.ILOSC) from MELDUNEKKART MK)) from MELDUNEK M group by 1;

    -- GROUP BY item which is an aggregate of the checked block, correlated with its own query block:
    select MK.ID_MELDUNEK, list(distinct (select M.ID_MELDUNEK from MELDUNEK M where M.ID_MELDUNEK = MK.ID_MELDUNEK), '') from MELDUNEKKART MK group by 1, 2;

    -- the same, in the WHERE clause:
    select 1 from MELDUNEK M where list(distinct (select MK.ILOSC from MELDUNEKKART MK), '') = 'x';

    select MK.ID_MELDUNEK from MELDUNEKKART MK where exists (select 1 from MELDUNEK M where M.ID_MELDUNEK = MK.ID_MELDUNEK and count(MK.ILOSC) > 0);
"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a WHERE clause, use HAVING (for aggregate only) instead
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a WHERE clause, use HAVING (for aggregate only) instead
"""

# Queries which must NOT be affected: an aggregate which is written inside a sub-select does not
# belong to the outer query block, and a field of the outer block used inside a correlated sub-select
# is an ordinary outer reference.
test_script_2 = init_isql + """
    select count(distinct MK.ILOSC) as n_dist, sum(distinct MK.ILOSC) as s_dist from MELDUNEKKART MK;

    select MK.ID_MELDUNEK, count(distinct MK.ILOSC) as n_dist from MELDUNEKKART MK group by 1 order by 1;

    -- LIST(DISTINCT ...) over a correlated sub-select, aggregate of the checked block but not in GROUP BY:
    select M.ID_MELDUNEK, cast(list(distinct (select max(MK.ILOSC) from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK), '|') as varchar(30)) as l_corr from MELDUNEK M group by 1 order by 1;

    -- SQL:2008: set function in a WHERE clause is allowed when its arguments are outer references:
    select M.ID_MELDUNEK from MELDUNEK M where exists (select count(*) from MELDUNEKKART MK where count(M.ID_MELDUNEK) > 0) order by 1;

    -- aggregate in HAVING, its argument is a correlated sub-select:
    select MK.ID_MELDUNEK from MELDUNEKKART MK group by 1 having count((select M.ID_MELDUNEK from MELDUNEK M where M.ID_MELDUNEK = MK.ID_MELDUNEK)) > 0 order by 1;

    -- aggregate in ORDER BY:
    select MK.ID_MELDUNEK from MELDUNEKKART MK group by 1 order by list(distinct (select M.ID_MELDUNEK from MELDUNEK M where M.ID_MELDUNEK = MK.ID_MELDUNEK), '');

    -- aggregate of a nested block which aggregates a field of the outer block:
    select MK.ID_MELDUNEK from MELDUNEKKART MK group by 1 having list(distinct (select M.ID_MELDUNEK from MELDUNEK M where M.ID_MELDUNEK = MK.ID_MELDUNEK), '') <> 'x' order by 1;

    -- window function must not be affected:
    select first 2 MK.ID_MELDUNEK, sum(MK.ILOSC) over () as s_all from MELDUNEKKART MK order by 1, 2;
"""

expected_stdout_2 = """
    N_DIST 4
    S_DIST 22
    ID_MELDUNEK 10376
    N_DIST 3
    ID_MELDUNEK 10377
    N_DIST 1
    ID_MELDUNEK 10376
    L_CORR 9
    ID_MELDUNEK 10377
    L_CORR 1
    ID_MELDUNEK 10376
    ID_MELDUNEK 10377
    ID_MELDUNEK 10376
    ID_MELDUNEK 10377
    ID_MELDUNEK 10376
    ID_MELDUNEK 10377
    ID_MELDUNEK 10376
    ID_MELDUNEK 10377
    ID_MELDUNEK 10376
    S_ALL 22
    ID_MELDUNEK 10376
    S_ALL 22
"""


# The same gap for the predicates whose sub-select is written inside the arguments of an
# aggregate: EXISTS, IN, SINGULAR and the quantified predicates are all RseBoolNode-s, and their
# fields must not be counted for the scope level of the aggregate either.
test_script_3 = init_isql + """
    -- the four variants reported as still crashing, see the issue:
    select list(distinct iif(exists(select 1 from MELDUNEKKART MK where MK.ID_PRODUKTZP is not null), 'T', 'N'), ';') from MELDUNEK M group by 1;

    select count(distinct iif(1 in (select MK.ID_PRODUKTZP from MELDUNEKKART MK), 1, 0)) from MELDUNEK M group by 1;

    select count(distinct iif(singular(select 1 from MELDUNEKKART MK where MK.ID_PRODUKTZP = 1), 1, 0)) from MELDUNEK M group by 1;

    select list(distinct iif(100 > all (select MK.ILOSC from MELDUNEKKART MK), 'T', 'N'), ';') from MELDUNEK M group by 1;

    -- the same gap outside the GROUP BY clause, both were accepted without an error before the fix:
    select M.ID_MELDUNEK from MELDUNEK M where sum(iif(exists(select 1 from MELDUNEKKART MK where MK.ILOSC > 0), 1, 0)) > 0;

    select max(count(iif(exists(select 1 from MELDUNEKKART MK where MK.ILOSC > 0), 1, 0))) from MELDUNEK M;

    -- aggregate without DISTINCT, cf. test_script_1:
    select count(iif(exists(select 1 from MELDUNEKKART MK), 1, 0)) from MELDUNEK M group by 1;

    -- negated and combined predicates:
    select list(distinct iif(not exists(select 1 from MELDUNEKKART MK), 'T', 'N'), ';') from MELDUNEK M group by 1;

    select list(distinct iif(exists(select 1 from MELDUNEKKART MK) and exists(select 1 from MELDUNEK M2), 'T', 'N'), ';') from MELDUNEK M group by 1;

    -- predicate whose left operand is a scalar sub-select:
    select list(distinct iif((select count(*) from MELDUNEKKART MK) in (select MK2.ID_PRODUKTZP from MELDUNEKKART MK2), 'T', 'N'), ';') from MELDUNEK M group by 1;

    -- quantified predicates, including the one rewritten by RseBoolNode::convertNeqAllToNotAny():
    select list(distinct iif(1 = any (select MK.ID_PRODUKTZP from MELDUNEKKART MK), 'T', 'N'), ';') from MELDUNEK M group by 1;

    select list(distinct iif(1 <> all (select MK.ID_PRODUKTZP from MELDUNEKKART MK), 'T', 'N'), ';') from MELDUNEK M group by 1;

    select list(distinct iif(not (1 = any (select MK.ID_PRODUKTZP from MELDUNEKKART MK)), 'T', 'N'), ';') from MELDUNEK M group by 1;

    -- predicate which contains a scalar sub-select, and a predicate inside a sub-select:
    select list(distinct iif(exists(select 1 from MELDUNEKKART MK where MK.ID_PRODUKTZP = (select max(MK2.ID_PRODUKTZP) from MELDUNEKKART MK2)), 'T', 'N'), ';') from MELDUNEK M group by 1;

    select count(distinct iif(1 in (select MK.ID_PRODUKTZP from MELDUNEKKART MK where exists (select 1 from MELDUNEK M2 where M2.ID_MELDUNEK = MK.ID_MELDUNEK)), 1, 0)) from MELDUNEK M group by 1;

    select count(distinct iif(exists(select 1 from MELDUNEKKART MK where MK.ID_PRODUKTZP is not null) or singular(select 1 from MELDUNEK M2), 1, 0)) from MELDUNEK M group by 1;

    -- the same, in the WHERE clause and as a nested aggregate:
    select 1 from MELDUNEK M where list(distinct iif(exists(select 1 from MELDUNEKKART MK), 'T', 'N'), ';') = 'T';

    select max(list(distinct iif(exists(select 1 from MELDUNEKKART MK), 'T', 'N'), ';')) from MELDUNEK M;

    -- the same, in the recursive member of a CTE:
    with recursive r as (select 1 as i from rdb$database union all select list(distinct iif(exists(select 1 from MELDUNEKKART MK), 'T', 'N'), ';') from r) select * from r;

    -- hypothetical-set aggregate, its sort item is a sub-select:
    select percentile_cont(0.5) within group (order by (select MK.ILOSC from MELDUNEKKART MK)) from MELDUNEK M group by 1;
"""

expected_stderr_3 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a WHERE clause, use HAVING (for aggregate only) instead
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Nested aggregate and window functions are not allowed
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a WHERE clause, use HAVING (for aggregate only) instead
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Nested aggregate and window functions are not allowed
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Recursive member of CTE cannot use aggregate or window function
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Cannot use an aggregate or window function in a GROUP BY clause
"""

# Queries of test_script_3 are rejected, so they say nothing about the aggregates which are placed
# in a legal position. These ones must stay valid and must keep returning the same values: a field
# of the checked block which is used inside a predicate sub-select (as the left operand of IN, or in
# the WHERE clause of that sub-select) is still seen by the checks, and aggregates of nested blocks
# which use fields of the outer block are not confused with aggregates of the outer block.
test_script_4 = init_isql + """
    -- DISTINCT aggregate whose argument is a correlated EXISTS:
    select count(distinct iif(exists(select 1 from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK and MK.ILOSC > 5), 1, 0)) as n1 from MELDUNEK M;

    select cast(list(distinct iif(exists(select 1 from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK and MK.ILOSC > 5), 'T', 'N'), '|') as varchar(10)) as l2 from MELDUNEK M;

    -- IN, its left operand is a field of the checked block:
    select cast(list(distinct iif(M.ID_MELDUNEK in (select MK.ID_MELDUNEK from MELDUNEKKART MK where MK.ILOSC > 3), 'T', 'N'), '|') as varchar(10)) as l3 from MELDUNEK M;

    -- SINGULAR and a quantified predicate:
    select count(distinct iif(singular(select MK.ILOSC from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK), 1, 0)) as n4 from MELDUNEK M;

    select cast(list(distinct iif(100 > all (select MK.ILOSC from MELDUNEKKART MK), 'T', 'N'), '|') as varchar(10)) as l5 from MELDUNEK M;

    -- EXISTS which itself contains a scalar sub-select with an aggregate of a nested block:
    select cast(list(distinct iif(exists(select 1 from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK and MK.ILOSC > (select avg(MK2.ILOSC) from MELDUNEKKART MK2 where MK2.ID_MELDUNEK = M.ID_MELDUNEK)), 'T', 'N'), '|') as varchar(10)) as l6 from MELDUNEK M;

    -- negated predicate and a predicate which contains a predicate:
    select cast(list(distinct iif(not exists(select 1 from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK), 'T', 'N'), '|') as varchar(10)) as l7 from MELDUNEK M;

    select count(distinct iif(1 in (select MK.ID_PRODUKTZP from MELDUNEKKART MK where exists (select 1 from MELDUNEK M2 where M2.ID_MELDUNEK = MK.ID_MELDUNEK)), 1, 0)) as n8 from MELDUNEK M;

    -- the checked block's aggregate with a GROUP BY, and with a field of its own block as well:
    select M.ID_MELDUNEK as i9, count(distinct iif(exists(select 1 from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK), 1, 0)) as n9 from MELDUNEK M group by 1 order by 1;

    select MK.ID_MELDUNEK as i10, cast(list(distinct iif(exists(select 1 from MELDUNEK M where M.ID_MELDUNEK = MK.ID_MELDUNEK) and MK.ILOSC > 5, 'T', 'N'), '') as varchar(10)) as l10 from MELDUNEKKART MK group by 1 order by 1;

    -- LIST(DISTINCT ...) over a correlated sub-select whose WHERE clause has a predicate sub-select:
    select M.ID_MELDUNEK as i11, cast(list(distinct (select max(MK.ILOSC) from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK and exists (select 1 from MELDUNEK M2 where M2.ID_MELDUNEK = MK.ID_MELDUNEK)), '|') as varchar(30)) as l11 from MELDUNEK M group by 1 order by 1;

    -- such aggregates in HAVING and in ORDER BY:
    select MK.ID_MELDUNEK as i12 from MELDUNEKKART MK group by 1 having count(distinct iif(exists(select 1 from MELDUNEK M where M.ID_MELDUNEK = MK.ID_MELDUNEK), 1, 0)) > 0 order by 1;

    select MK.ID_MELDUNEK as i13 from MELDUNEKKART MK group by 1 having count(distinct iif(exists(select 1 from MELDUNEKKART MK2 where MK2.ID_MELDUNEK = MK.ID_MELDUNEK and MK2.ILOSC > MK.ILOSC), 1, 0)) = 2 order by 1;

    select MK.ID_MELDUNEK as i14 from MELDUNEKKART MK group by 1 order by list(distinct iif(exists(select 1 from MELDUNEKKART MK2 where MK2.ID_MELDUNEK = MK.ID_MELDUNEK and MK2.ILOSC > MK.ILOSC), 'T', 'N'), '') desc, 1;

    -- aggregate of a nested block, its argument contains a predicate sub-select:
    select MK.ID_MELDUNEK as i15, (select count(distinct iif(exists(select 1 from MELDUNEK M2 where M2.ID_MELDUNEK = MK.ID_MELDUNEK and MK2.ILOSC > 5), 1, 0)) from MELDUNEKKART MK2 where MK2.ID_MELDUNEK = MK.ID_MELDUNEK) as n15 from MELDUNEKKART MK group by 1 order by 1;

    select MK.ID_MELDUNEK as i16, (select count(distinct iif(exists(select 1 from MELDUNEK M2 where M2.ID_MELDUNEK = MK2.ID_MELDUNEK), 1, 0)) from MELDUNEKKART MK2 where MK2.ID_MELDUNEK = MK.ID_MELDUNEK) as n16 from MELDUNEKKART MK group by 1 order by 1;

    -- window function with a predicate sub-select in its argument:
    select first 2 MK.ID_MELDUNEK as i17, sum(iif(exists(select 1 from MELDUNEK M where M.ID_MELDUNEK = MK.ID_MELDUNEK), 1, 0)) over () as s17 from MELDUNEKKART MK order by 1, 2;

    -- aggregate of the checked block in the select list of a sub-select:
    select M.ID_MELDUNEK as i18, (select count(distinct iif(exists(select 1 from MELDUNEKKART MK where MK.ID_MELDUNEK = M.ID_MELDUNEK and MK.ILOSC > 5), 1, 0)) from rdb$database) as n18 from MELDUNEK M order by 1;
"""

expected_stdout_4 = """
    N1 2
    L2 N|T
    L3 N|T
    N4 2
    L5 T
    L6 N|T
    L7 N
    N8 1
    I9 10376
    N9 1
    I9 10377
    N9 1
    I10 10376
    L10 NT
    I10 10377
    L10 N
    I11 10376
    L11 9
    I11 10377
    L11 1
    I12 10376
    I12 10377
    I13 10376
    I14 10377
    I14 10376
    I15 10376
    N15 2
    I15 10377
    N15 1
    I16 10376
    N16 1
    I16 10377
    N16 1
    I17 10376
    S17 4
    I17 10376
    S17 4
    I18 10376
    N18 1
    I18 10377
    N18 1
"""

act_1 = isql_act('db', test_script_1, substitutions=substitutions)
act_2 = isql_act('db', test_script_2, substitutions=substitutions)
act_3 = isql_act('db', test_script_3, substitutions=substitutions)
act_4 = isql_act('db', test_script_4, substitutions=substitutions)


@pytest.mark.ai
@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == ''


@pytest.mark.ai
@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout
    assert act_2.clean_stderr == ''


@pytest.mark.ai
@pytest.mark.version('>=4.0')
def test_3(act_3: Action):
    act_3.expected_stderr = expected_stderr_3
    act_3.execute()
    assert act_3.clean_stderr == act_3.clean_expected_stderr
    assert act_3.clean_stdout == ''


@pytest.mark.ai
@pytest.mark.version('>=4.0')
def test_4(act_4: Action):
    act_4.expected_stdout = expected_stdout_4
    act_4.execute()
    assert act_4.clean_stdout == act_4.clean_expected_stdout
    assert act_4.clean_stderr == ''
