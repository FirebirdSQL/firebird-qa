#coding:utf-8
#
# id:           bugs.core_3925
# title:        Creating self-referential FK crashes database (bug-check) whether constraint violation had place
# decription:   
#                   Confirmed on WI-V3.0.5.33118, WI-T4.0.0.1496: "SQLSTATE = 08006 / Error reading..." on last DELETE statement
#                   Checked on WI-V3.0.5.33123, WI-T4.0.0.1501 (both SS an CS): works OK, got only SQLSTATE = 23000 when try to add FK.
#                   DELETE statement does not raise error.
#                
# tracker_id:   CORE-3925
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table test(key integer not null primary key, ref integer);
    insert into test(key,ref) values(1,-1);
    commit;
    alter table test add constraint fk_key_ref foreign key (ref) references test(key);
    delete from test;
    commit; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "FK_KEY_REF" on table "TEST"
    -Foreign key reference target does not exist
    -Problematic key value is ("REF" = -1)
  """

@pytest.mark.version('>=3.0.5')
def test_core_3925_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

