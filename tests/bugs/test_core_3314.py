#coding:utf-8
#
# id:           bugs.core_3314
# title:        Dependencies are not removed after dropping the procedure and the table it depends on in the same transaction
# decription:   
# tracker_id:   CORE-3314
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """create table t (a int);
SET TERM !!;
create procedure p as begin delete from t; end!!
SET TERM !!;
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT 1 FROM  RDB$DEPENDENCIES WHERE RDB$DEPENDED_ON_NAME='T';
drop procedure p;
drop table t;
commit;
SELECT 1 FROM  RDB$DEPENDENCIES WHERE RDB$DEPENDED_ON_NAME='T';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_3314.fdb, User: SYSDBA
SQL>
    CONSTANT
============
           1

SQL> SQL> SQL> SQL> SQL>"""

@pytest.mark.version('>=2.5.1')
def test_core_3314_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

