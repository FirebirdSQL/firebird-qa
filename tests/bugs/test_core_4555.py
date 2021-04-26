#coding:utf-8
#
# id:           bugs.core_4555
# title:        DDL trigger remains active after dropped
# decription:   
# tracker_id:   CORE-4555
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', ''), ('line:\\s[0-9]+,', 'line: x'), ('col:\\s[0-9]+', 'col: y')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create exception ddl_exception 'You have no right to create exceptions. Learn DDL triggers first!';
    commit;
    set term ^;
    create or alter trigger t_ddl
    active before create exception
    as
    begin
      if (current_user <> 'DUDE') then
        exception ddl_exception;
    end
    ^
    set term ;^
    commit;

    create exception user_exception 'Invalid remainder found for case-1.';
    commit;
    
    drop trigger t_ddl;
    commit;

    create exception user_exception 'Invalid remainder found for case-2.'
    ;
    commit;

    set list on;
    set count on;
    select rdb$exception_name, rdb$message 
    from rdb$exceptions
    order by rdb$exception_name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$EXCEPTION_NAME              DDL_EXCEPTION                                                                                                                                                                                                                                                              
    RDB$MESSAGE                     You have no right to create exceptions. Learn DDL triggers first!

    RDB$EXCEPTION_NAME              USER_EXCEPTION                                                                                                                                                                                                                                                              
    RDB$MESSAGE                     Invalid remainder found for case-2.

    Records affected: 2
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    unsuccessful metadata update
    -CREATE EXCEPTION USER_EXCEPTION failed
    -exception 1
    -DDL_EXCEPTION
    -You have no right to create exceptions. Learn DDL triggers first!
    -At trigger 'T_DDL' line: 6, col: 9
  """

@pytest.mark.version('>=3.0')
def test_core_4555_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

