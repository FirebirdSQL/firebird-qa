#coding:utf-8
#
# id:           bugs.core_3691
# title:        Missing constraint name in foreign key error message in FB 2.1.4
# decription:   
# tracker_id:   CORE-3691
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    --  Note. Info about problematic key exists since 2.5.3
    recreate table tmain(id int primary key using index tmain_pk);
    commit;
    insert into tmain values(1);
    commit;
    recreate table tdetl(id int primary key using index tdetl_pk, pid int);
    commit;
    insert into tdetl values(1,2);
    commit;
    alter table tdetl add constraint tdetl_fk foreign key(pid) references tmain(id);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "TDETL_FK" on table "TDETL"
    -Foreign key reference target does not exist
    -Problematic key value is ("PID" = 2)
  """

@pytest.mark.version('>=2.5.3')
def test_core_3691_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

