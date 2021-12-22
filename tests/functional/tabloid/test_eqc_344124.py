#coding:utf-8
#
# id:           functional.tabloid.eqc_344124
# title:        Check ability to run selectable SP with input parameter which inserts into GTT (on commit DELETE rows) and then does suspend
# decription:   NB: if either a_id, suspend or the insert is removed, or if gtt_test is changed to on commit preserve rows - no crash
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate global temporary table gtt_test (
        id  integer
    ) on commit delete rows;
    
    set term  ^;
    create procedure test
    returns (
        o_id integer)
    as
    begin
      insert into gtt_test(id) values( 1 + rand() * 100 ) returning sign(id) into o_id;
      --o_id = 0;
      suspend;
    end
    ^
    set term ;^
    commit;
    
    set list on;
    select * from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    O_ID                            1
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

