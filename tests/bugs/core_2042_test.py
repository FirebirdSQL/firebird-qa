#coding:utf-8
#
# id:           bugs.core_2042
# title:        connection lost to database when used AUTONOMOUS TRANSACTION
# decription:   
# tracker_id:   CORE-2042
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    create or alter procedure test_caller_name
    returns (
        object_name char(31),
        object_type smallint)
    as
    begin
    end
    ^
    create or alter procedure get_caller_name
    returns (
        object_name char(31),
        object_type smallint)
    as
    declare variable tran_id integer;
    begin
      tran_id = current_transaction;
    
      in autonomous transaction do
      begin
        select cs.mon$object_name, cs.mon$object_type
          from mon$call_stack cs, mon$statements st
         where cs.mon$statement_id = st.mon$statement_id
               and st.mon$transaction_id = :tran_id
               and cs.mon$caller_id is null -- :: nb :: Added this condition because output differs in 3.0 vs 2.5!
          order by cs.mon$call_id
          rows 1
        into :object_name, :object_type;
      end
    
      suspend;
    end
    ^
    
    create or alter procedure test_caller_name
    returns (
        object_name char(31),
        object_type smallint)
    as
    begin
      select object_name, object_type from get_caller_name
         into :object_name, :object_type;
    
      suspend;
    end
    ^
    set term ;^
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select * from test_caller_name;
    select * from test_caller_name;
    select * from test_caller_name;
    select * from test_caller_name;
    select * from test_caller_name;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    OBJECT_NAME                     TEST_CALLER_NAME               
    OBJECT_TYPE                     5
    OBJECT_NAME                     TEST_CALLER_NAME               
    OBJECT_TYPE                     5
    OBJECT_NAME                     TEST_CALLER_NAME               
    OBJECT_TYPE                     5
    OBJECT_NAME                     TEST_CALLER_NAME               
    OBJECT_TYPE                     5
    OBJECT_NAME                     TEST_CALLER_NAME               
    OBJECT_TYPE                     5
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

