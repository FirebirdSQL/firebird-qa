#coding:utf-8
#
# id:           bugs.core_3244
# title:        POSITION: Wrong result with '' if third argument present
# decription:   
# tracker_id:   CORE-3244
# min_versions: ['2.1.4']
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select position ('', 'Broehaha') from rdb$database;
select position ('', 'Broehaha', 4) from rdb$database;
select position ('', 'Broehaha', 20) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_3244.fdb, User: SYSDBA
SQL>
    POSITION
============
           1

SQL>
    POSITION
============
           4

SQL>
    POSITION
============
           0

SQL>"""

@pytest.mark.version('>=2.1.4')
def test_core_3244_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

