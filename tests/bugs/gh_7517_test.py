#coding:utf-8

"""
ID:          issue-7517
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7517
TITLE:       Successful compiling of procedure with wrong PLAN(s) used by some of its statement(s)
NOTES:
    [29.03.2023] pzotov
    Code for reproducing was provided by dimitr, letter 29.03.2023 09:46.
	Confirmed bug on 3.0.11.33665.
    Cheched on 5.0.0.978; 4.0.3.2913; 3.0.11.33666 - all fine.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t1 (id int, fld int);
    recreate table t2 (id int, fld int);
    create index t1_id on t1 (id);
    create index t2_id on t2 (id);
    create index t2_fld on t2 (fld);

    select
        t1.fld
       ,( select t2.fld
          from t2
          where t2.id = t1.id
          plan (t2 index (t2_fld, t2_id))
        )
    from t1;
"""

expected_stdout = """
    Statement failed, SQLSTATE = 42000
    index T2_FLD cannot be used in the specified plan
"""

act = isql_act('db', test_script)

@pytest.mark.version('>=3.0.11')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
