#coding:utf-8
#
# id:           functional.table.create.07
# title:        CREATE TABLE - unknown datatype (domain)
# decription:   CREATE TABLE - unknown datatype (domain)
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.table.create.create_table_07

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """CREATE TABLE test(
 c1 unk_domain
);"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-CREATE TABLE TEST failed
-SQL error code = -607
-Invalid command
-Specified domain or source column UNK_DOMAIN does not exist

"""

@pytest.mark.version('>=3.0')
def test_07_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

