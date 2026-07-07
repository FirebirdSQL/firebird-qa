#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/bf10ae16d57aabdbb2145dd528d44f44144098e9
TITLE:       CTAS. Allow the use of parenthesis in CREATE TABLE AS (...)
DESCRIPTION:
NOTES:
    [07.07.2026] pzotov
    Discussion: https://groups.google.com/g/firebird-devel/c/qR0DINRSs28/m/-kWVYrk2AQAJ
    Checked on 6.0.0.2067-bf10ae1
"""
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    test_script = f"""
        set bail OFF;
        set autoddl off;
        set autoterm  on;
        commit;
        create table employee (
            emp_no int,
            dept_no int,
            salary numeric(10,2)
        );
        insert into employee select i, mod(i,30), 10000 + rand()*30000
        from generate_series(1, 1000, 1) as u(i);
        create unique index e_emp_no on employee(emp_no);
        create index e_dept_no on employee(dept_no);
        commit;
        --------------------------------------------------------------------------------------------
        -- Examples from https://groups.google.com/g/firebird-devel/c/qR0DINRSs28/m/-kWVYrk2AQAJ
        recreate table ctas_test_001 as (
            (select rdb$relation_name from rdb$relations order by 1 desc) rows 1
        );

        recreate table ctas_test_005 as (
            (select rdb$relation_name from rdb$relations order by 1 desc fetch first row only)
        );

        recreate table ctas_test_010 as (
            (select rdb$relation_name from rdb$relations order by 1 desc) fetch first row only
        );
        --------------------------------------------------------------------------------------------
        -- Examples from misc drafts:
        recreate table ctas_test_010 as (
            (select rdb$relation_name from rdb$relations PLAN ("SYSTEM"."RDB$RELATIONS" NATURAL))
        );

        recreate table ctas_test_015 as (
            (
                select
                  *
                from (select rdb$relation_name, rdb$relation_id from rdb$relations) as r (relation_name, relation_id)
                cross join lateral
                    (select count(*) from rdb$relation_fields where rdb$relation_name = r.relation_name) as rf (field_count)
            )
        );

        recreate table ctas_test_020 as (
            (
                select u.* from unlist('6,7,8,9,0' returning int) as u(example_02)
            )
        );

        recreate table ctas_test_025 as (
            (
                select * from generate_series(9223372036854775806, 9223372036854775807, 1) as place_holder_name( generated_values_010 )
            ) rows (1+2+3+4+5+6*2/4-3-2-1)
        );

        recreate table ctas_test_030 as (
            (
                select emp_no, salary, 'lowest' as type
                from employee
                order by salary asc
                fetch first row only
            )
            union all
            (
                select emp_no, salary, 'highest' as type
                from employee
                order by salary desc
                fetch first row only
            )
        );

        recreate table ctas_test_035 as (
            select
                emp_no,
                dept_no,
                salary,
                count(*)over w1                                  as cnt_over_rw1,
                first_value(salary)over w2                       as first_over_w2,
                last_value(salary)over w2                        as last_over_w2,
                sum(salary)over(
                    w2 rows between current row and 1 following
                )                                                as sum_over_rows_btwn
            from employee
            window
                w1 as (partition by dept_no),
                w2 as (w1 order by salary)
            order by dept_no, salary
        );
        --------------------------------------------------------------------------------------------
        -- Example from https://groups.google.com/g/firebird-devel/c/QgkYzbMVgow/m/7Q1iKgfEAAAJ
        recreate table tmp_factorial as (
            with recursive
            r1 as (
                select 1 i, cast(1 as decfloat(34)) f from rdb$database
                union all
                select r.i+1, r.f * (r.i+1) from r1 as r where r.i < 1024
            )
            select * from r1
        )
        with data
        ;

    """

    act.expected_stdout = """
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
