#coding:utf-8
#
# id:           bugs.core_1875
# title:        Error on script with current_date
# decription:   
#                   Confirmed bug on: 2.1.0.17798, result was:
#                   ===
#                       Statement failed, SQLCODE = -902
#                       Unable to complete network request to host "localhost".
#                       -Error reading data from the connection.
#                       Connection rejected by remote interface
#                   ===
#                   Works fine on: 2.1.1.17910.
#                   Also checked on:
#                       build 2.5.9.27107: OK, 0.391s.
#                       build 3.0.4.32924: OK, 2.610s.
#                       build 4.0.0.916: OK, 1.515s.
#                   PS. 
#                   It seems that bug was somehow related to "if" statement. For example, following statements:
#                       select 1 from new_table nt where nt.data_reg = cast(current_date as date) into c;
#                   or:
#                       select 1 from rdb$database
#                       where not exists(
#                           select 1 from new_table nt where nt.data_reg = cast(current_date as date)
#                       )
#                       into c;
#                   -- finished without errors.
#                
# tracker_id:   CORE-1875
# min_versions: ['2.1.0']
# versions:     2.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table new_table (
        data_reg timestamp -- can be used in this test instead of type 'date' (result the same: 2.1.0 crashes)
    );
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    execute block returns(msg varchar(10)) as
        declare c int;
    begin
        if ( exists( select 1 from new_table nt where nt.data_reg = cast(current_date as date) ) ) then
            begin
            end
        msg = 'Done';
        suspend;
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             Done
  """

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

