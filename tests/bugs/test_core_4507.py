#coding:utf-8
#
# id:           bugs.core_4507
# title:        Unable delete procedure source on Firebird 3.0 Alpha 2.0
# decription:   
# tracker_id:   CORE-4507
# min_versions: ['2.0.7']
# versions:     2.0.7
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = [('RDB\\$PROCEDURE_SOURCE.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create or alter procedure sp_test(x int, y int) returns(z bigint) as
    begin
       z = x + y;
       suspend;
    end
    ^set term ;^
    commit;
    
    set blob all;
    set list on;
    select rdb$procedure_source from rdb$procedures where rdb$procedure_name = upper('sp_test');
    
    update rdb$procedures set rdb$procedure_source = null where rdb$procedure_name = upper('sp_test');
    commit;
    select iif(rdb$procedure_source is null, 'NO_SOURCE', 'HAS_SOURCE') sp_src from rdb$procedures where rdb$procedure_name = upper('sp_test');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    begin
       z = x + y;
       suspend;
    end
    SP_SRC                          NO_SOURCE
  """

@pytest.mark.version('>=2.0.7')
def test_core_4507_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

