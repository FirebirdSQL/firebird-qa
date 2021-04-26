#coding:utf-8
#
# id:           bugs.core_3058
# title:        New generators are created with wrong value when more than 32K generators was previously created
# decription:   
# tracker_id:   CORE-3058
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    execute block
    as
        declare n int = 1;
        declare x int;
        declare k int;
        declare c int;
    begin
        while (n < 33000) do
        begin
          k = 1000000 + cast(rand() * 1000000 as int);

          -- ::: NB ::: As of Firebird 3.0 we need to make EVERY operation (creation, select gen_id, dropping)
          -- in AUTONOMOUS transaction because physically appearance of generator in database will be on COMMIT only.
          -- It is not so in 2.5, but I left code common for both FB versions. Zotov.
          in autonomous transaction do
            execute statement 'create sequence s' || n;
    
          in autonomous transaction do
            execute statement 'select gen_id(s' || n || ', ' || k || ') from rdb$database' into x;
    
          in autonomous transaction do
            execute statement 'drop sequence s' || n;
    
          n = n + 1;
        end
    end
    ^
    set term ;^
    rollback;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Updated code: remove dependency on: 1) version FB and 2) output of 'show sequence' command.
    -- Also we check here that NO sequences exists at this point and after we create and drop sequence 's1'
    set list on;
    select iif( exists(select * from rdb$generators g where coalesce(g.rdb$system_flag,0) = 0), 'some_gen_exists!', 'none_gen_remains' ) as msg_1
    from rdb$database;
    create sequence s1;
    commit;
    select gen_id(s1,0) as current_val_of_s1 from rdb$database;
    commit;
    drop sequence s1;
    commit;
    select iif( exists(select * from rdb$generators g where coalesce(g.rdb$system_flag,0) = 0), 'some_gen_exists!', 'none_gen_remains' ) as msg_2
    from rdb$database;
    set list off;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG_1                           none_gen_remains
    CURRENT_VAL_OF_S1               0
    MSG_2                           none_gen_remains
  """

@pytest.mark.version('>=2.5.1')
@pytest.mark.slow
def test_core_3058_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

