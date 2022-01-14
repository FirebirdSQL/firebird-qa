#coding:utf-8
#
# id:           bugs.core_2916
# title:        Broken error handling in the case of a conversion error happened during index creation
# decription:
# tracker_id:   CORE-2916
# min_versions: ['2.1.4']
# versions:     2.5.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', '2011-05-03')]

init_script_1 = """create table tab (col date);
insert into tab (col) values (current_date);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """create index itab on tab computed (cast(col as int));
commit;
select * from tab where cast(col as int) is null;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\fbtest2\\tmp\\bugs.core_2916.fdb, User: SYSDBA
SQL> SQL> SQL>
        COL
===========
SQL>"""
expected_stderr_1 = """Statement failed, SQLSTATE = 22018

conversion error from string "2011-05-03"

Statement failed, SQLSTATE = 22018

conversion error from string "2011-05-03"
"""

@pytest.mark.version('>=2.5.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    recreate table tab (col date);
    insert into tab (col) values ( date '29.02.2004' );
    commit;

    create index itab on tab computed (cast(col as int));
    commit;
    set list on;
    select * from tab where cast(col as int) is null;
"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

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

