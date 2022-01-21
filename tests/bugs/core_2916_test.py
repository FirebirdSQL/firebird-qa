#coding:utf-8

"""
ID:          issue-3300
ISSUE:       3300
TITLE:       Broken error handling in the case of a conversion error happened during index creation
DESCRIPTION:
JIRA:        CORE-2916
"""

import pytest
from firebird.qa import *

# version: 3.0

init_script_1 = """create table tab (col date);
insert into tab (col) values (current_date);
commit;
"""

db_1 = db_factory(init=init_script_1)

test_script_1 = """create index itab on tab computed (cast(col as int));
commit;
select * from tab where cast(col as int) is null;"""

act_1 = isql_act('db_1', test_script_1,
                 substitutions=[('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', '2011-05-03')])

expected_stdout_1 = """
        COL
===========
"""

expected_stderr_1 = """Statement failed, SQLSTATE = 22018

conversion error from string "2011-05-03"

Statement failed, SQLSTATE = 22018

conversion error from string "2011-05-03"
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert (act_1.clean_stderr == act_1.clean_expected_stderr and
            act_1.clean_stdout == act_1.clean_expected_stdout)

# version: 4.0

db_2 = db_factory()

test_script_2 = """
    recreate table tab (col date);
    insert into tab (col) values ( date '29.02.2004' );
    commit;

    create index itab on tab computed (cast(col as int));
    commit;
    set list on;
    select * from tab where cast(col as int) is null;
"""

act_2 = isql_act('db_2', test_script_2)

expected_stderr_2 = """
    Statement failed, SQLSTATE = 22018
    Expression evaluation error for index "***unknown***" on table "TAB"
    -conversion error from string "2004-02-29"
    Statement failed, SQLSTATE = 22018
    conversion error from string "2004-02-29"
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_stderr == act_2.clean_expected_stderr

