#coding:utf-8
#
# id:           bugs.core_3003
# title:        Procedure suspend check may cause restore to fail
# decription:   
#                   Checked on:
#                       2.5.9.27126: OK, 0.859s.
#                       3.0.5.33086: OK, 1.937s.
#                       4.0.0.1378: OK, 7.516s.
#                
# tracker_id:   CORE-3003
# min_versions: ['2.1']
# versions:     2.1
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = [('RDB\\$PROCEDURE_SOURCE.*', '')]

init_script_1 = """"""

db_1 = db_factory(from_backup='c3003-ods11.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    select rdb$procedure_name, rdb$procedure_source 
    from rdb$procedures 
    where upper( rdb$procedure_name ) in ( upper('sp_01'), upper('sp_02') )
    order by rdb$procedure_name
    ;

    select RDB$PROCEDURE_NAME, RDB$PARAMETER_NAME, RDB$PARAMETER_TYPE,RDB$PARAMETER_MECHANISM 
    from rdb$procedure_parameters
    where upper( rdb$procedure_name ) in ( upper('sp_01'), upper('sp_02') )
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$PROCEDURE_NAME              SP_01
    RDB$PROCEDURE_SOURCE            1a:1
    begin
      n = 1;
    end
    
    RDB$PROCEDURE_NAME              SP_02
    RDB$PROCEDURE_SOURCE            1a:4
    declare n int;
    begin
      select n from sp_01 into n;
    end
    
    RDB$PROCEDURE_NAME              SP_01
    RDB$PARAMETER_NAME              N
    RDB$PARAMETER_TYPE              1
    RDB$PARAMETER_MECHANISM         0
  """

@pytest.mark.version('>=2.1')
def test_core_3003_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

