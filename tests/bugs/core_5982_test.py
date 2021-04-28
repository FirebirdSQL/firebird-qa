#coding:utf-8
#
# id:           bugs.core_5982
# title:        error read permission for BLOB field, when it is input/output procedure`s parametr
# decription:   
#                   Confirmed bug on WI-V3.0.4.33034 and WI-T4.0.0.1340.
#                   Checked on:
#                       4.0.0.1421: OK, 2.098s.
#                       3.0.5.33097: OK, 1.294s.
#               
#                   24.06.2020: changed min_version to 2.5 because problem was fixed in 2.5.9.27151.
#                
# tracker_id:   CORE-5982
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    set term ^;
    execute block as
    begin
        begin
            execute statement 'drop user tmp$c5982' with autonomous transaction;
            when any do begin end
        end
    end^
    set term ;^
    commit;


    create user tmp$c5982 password '123';
    commit;
    recreate table my_table ( 
       my_num integer
      ,my_data blob
    );
    commit;

    insert into my_table(my_num , my_data) values (1, 'qwerty');
    commit;

    set term ^;
    create or alter procedure sp_worker(my_data blob) as
        declare variable my_value blob;
    begin
        my_value = my_data ;
        rdb$set_context('USER_SESSION', 'SP_WORKER', 'DONE BY ' || current_user );
    end
    ^

    create or alter procedure sp_main as
        declare variable my_data blob;
    begin
        select my_data
          from my_table
         where my_num = 1
         into: my_data;

         execute procedure sp_worker(my_data);

    end
    ^
    set term ;^
    commit;

    grant select on table my_table to procedure sp_main;
    grant execute on procedure sp_worker to procedure sp_main;
    grant execute on procedure sp_main to public;
    commit;

    set list on;

    connect '$(DSN)' user 'tmp$c5982' password '123';

    execute procedure sp_main;
    select rdb$get_context('USER_SESSION', 'SP_WORKER') as result from rdb$database;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user tmp$c5982;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT                          DONE BY TMP$C5982
  """

@pytest.mark.version('>=2.5.9')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

