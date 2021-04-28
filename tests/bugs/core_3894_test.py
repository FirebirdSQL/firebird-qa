#coding:utf-8
#
# id:           bugs.core_3894
# title:        Wrong numbers in error message for decreasing char/varchar columns
# decription:   
# tracker_id:   CORE-3894
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set autoddl off;
    recreate table test(id int);
    commit;

    alter table test add s01 varchar(8188) character set utf8;
    commit;

    alter table test alter column s01 type varchar(8189) character set utf8;
    alter table test alter column s01 type varchar(8190) character set utf8;
    alter table test alter column s01 type varchar(8189) character set utf8;
    commit;

    show table test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              INTEGER Nullable 
    S01                             VARCHAR(8190) CHARACTER SET UTF8 Nullable 
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE TEST failed
    -New size specified for column S01 must be at least 8190 characters.
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

