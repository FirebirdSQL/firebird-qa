#coding:utf-8
#
# id:           bugs.core_3594
# title:        Include expected and actual string lenght into error message for sqlcode -802
# decription:   
# tracker_id:   CORE-3594
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('line: .*', 'line'), ('col: .*', 'col')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter procedure sp_overflowed_1 as begin end;
    set term ^;
    create or alter procedure sp_detailed_info returns(msg varchar(60)) as
    begin
        msg = '....:....1....:....2....:....3....:....4....:....5....:....6';
        suspend;
    end
    ^
    
    create or alter procedure sp_overflowed_1 returns(msg varchar(50)) as
    begin
        execute procedure sp_detailed_info returning_values msg;
        suspend;
    end
    
    ^
    create or alter procedure sp_overflowed_2 returns(msg varchar(59)) as
    begin
        msg = '....:....1....:....2....:....3....:....4....:....5....:....6';
        suspend;
    end
    ^
    set term ;^
    commit;
    
    set heading off;
    select * from sp_overflowed_1;
    select * from sp_overflowed_2;

    -- On 2.5.x info about expected and actual length is absent:
    -- Statement failed, SQLSTATE = 22001
    -- arithmetic exception, numeric overflow, or string truncation
    -- -string right truncation
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22001
    arithmetic exception, numeric overflow, or string truncation
    -string right truncation
    -expected length 50, actual 60
    -At procedure 'SP_OVERFLOWED_1' line: 3, col: 5
    
    Statement failed, SQLSTATE = 22001
    arithmetic exception, numeric overflow, or string truncation
    -string right truncation
    -expected length 59, actual 60
    -At procedure 'SP_OVERFLOWED_2' line: 3, col: 5
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

