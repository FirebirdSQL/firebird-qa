#coding:utf-8
#
# id:           functional.gtcs.computed_fields_15
# title:        computed-fields-15
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_15.script
#               	SQL script for creating test database ('gtcs_sp1.fbk') and fill it with some data:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROCS_QA_INIT_ISQL.script
#                   Checked on: 4.0.0.1803 SS; 3.0.6.33265 SS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('^((?!Statement failed|SQL error code).)*$', ''), (' = ', ' '), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    /*-----------------------------------------------------------------------------*/
    /* Create a table with computed field which is defined using non-existing UDF. */
    /*-----------------------------------------------------------------------------*/
    create table t0 (a integer, af computed by ( non_exist_udf(a) ));
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE 39000
    Dynamic SQL Error
    -SQL error code -804
    -Function unknown
    -NON_EXIST_UDF
  """

@pytest.mark.version('>=2.5')
def test_computed_fields_15_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

