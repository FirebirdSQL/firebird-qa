#coding:utf-8

"""
ID:          issue-5830
ISSUE:       5830
TITLE:       Use exception instead bugcheck for EVL_expr
DESCRIPTION:
NOTES:
    [19.06.2018] pzotov
    Ability to use nested aggregate looks strange.
    Query like here can not be run in MS SQL or Postgress.
    Sent letters to dimitr, 19.06.2018.

    [06.11.2026] pzotov
    DISABLED execution on 6.x: since some recent commit, this test fails with
    "SQLSTATE = 42000/  -Nested aggregate and window functions are not allowed".
    This behaviour *MEETS* requirements of SQL standard, see "SQL:2011 Foundation,
    Subclause 6.9 <set function specification>, Syntax Rule 1 (PDF page 238)":
    "If <aggregate function> specifies a <general set function>,
     then the <value expression> simply contained in the <general set function>
     shall not contain a <set function specification> or a <query expression>."
JIRA:        CORE-5563
FBTEST:      bugs.core_5563
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    select
        sum(
            sum(
                (select sum(rf.rdb$field_position) from rdb$relation_fields rf)
               )
           )
    from
        rdb$database
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
    SUM                             <null>
"""

@pytest.mark.version('>=3.0,<6')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
