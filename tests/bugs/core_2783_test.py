#coding:utf-8

"""
ID:          issue-3174
ISSUE:       3174
TITLE:       AV using recursive query as subquery in SELECT list and ORDER'ing by them
DESCRIPTION:
JIRA:        CORE-2783
NOTES:
    [14.06.2026] pzotov
    Changed query to reproduce problem: on 6.x we have to avoid referring of RDB$DATABASE.RDB$RELATION_ID
    because GENERATOR is used to store generated relation_id instead of this field, see #bb280120.

    Confirmed bug on 2.1.3.18185 (check possible only using command prompt and ISQL; not in this QA).
    Checked on 2.1.7.18553 -- all fine.

    Checked on 6.0.0.2002; 5.0.5.1826; 4.0.8.3279; 3.0.14.33855.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    recreate table test(id int);
    insert into test(id) values(128);
    commit;

    select
        1 as qry
        ,(
             with recursive
             num (id) as
             (
                 select 1 from test
                 UNION ALL
                 select id + 1
                 from num
                 where id < 10
             )
            select max(id) from num
        ) as nnn
    from test
    order by nnn;

    with recursive
      num (id) as
      (
               select 1 from test

               union all

               select id + 1
                 from num
                where id < 10
      )
    select 2 as qry, (select max(id) from num) as nnn
    from test
    order by nnn;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    QRY 1
    NNN 10
    QRY 2
    NNN 10
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
