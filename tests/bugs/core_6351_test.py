#coding:utf-8
#
# id:           bugs.core_6351
# title:        Computed field could be wrongly evaluated as NULL
# decription:   
#                   Confirmed bug on 4.0.0.2087.
#                   Checked on 4.0.0.2170, 3.0.7.33357 -- all fine.
#                 
# tracker_id:   
# min_versions: ['3.0.7']
# versions:     3.0.7
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.7
# resources: None

substitutions_1 = []

init_script_1 = """
    create table t1
    (
      id int,
      f1 computed by ('abcd'),
      f2 computed by ('xyz')
    );
    commit;

    set term ^;
    create or alter procedure p_t1 (id int)
      returns (val varchar(32))
    as
    begin
      val = 'unknown';

      select f2 from t1 where id = :id
        into :val;

      suspend;
    end^
    set term ;^
    commit;

    alter table t1
      alter f1 computed by ((select val from p_t1(id)));

    alter table t1
      alter f2 computed by ('id = ' || id);
    commit;

    insert into t1 values (1);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select 'case-1' as msg, p.val from p_t1(1) p;
    select t.* from t1 t;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';

    select t.* from t1 t;
    select 'case-2' as msg, p.val from p_t1(1) p;
    exit; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             case-1
    VAL                             id = 1
    ID                              1
    F1                              id = 1
    F2                              id = 1

    ID                              1
    F1                              id = 1
    F2                              id = 1
    MSG                             case-2
    VAL                             id = 1
  """

@pytest.mark.version('>=3.0.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

