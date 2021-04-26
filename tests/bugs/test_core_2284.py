#coding:utf-8
#
# id:           bugs.core_2284
# title:        Records left in RDB$PAGES after rollback of CREATE TABLE statement
# decription:   
#                   This test also covers issues of CORE-5677.
#                   Bug confirmed on: 3.0.3.32837, 4.0.0.800
#                   Checked on:
#                       3.0.3.32854: OK, 1.968s.
#                       4.0.0.832: OK, 1.282s.
#                
# tracker_id:   CORE-2284
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set autoddl off;
    recreate table test_cs__master (
        str_pk varchar(32) character set UTF8 not null,
        primary key (str_pk) using index test_s_master_pk
    );

    recreate table test_cs__detail (
        str_pk varchar(32) character set WIN1251 not null,
        foreign key (str_pk) references test_cs__master (str_pk)
    );

    commit; -- this will raise: "SQLSTATE = 42000 / -partner index segment no 1 has incompatible data type"

    rollback;

    set list on;

    select count(*) 
    from rdb$pages 
    where rdb$relation_id >= (select rdb$relation_id from rdb$database);

    rollback;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COUNT                           0
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -partner index segment no 1 has incompatible data type
  """

@pytest.mark.version('>=3.0.3')
def test_core_2284_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

