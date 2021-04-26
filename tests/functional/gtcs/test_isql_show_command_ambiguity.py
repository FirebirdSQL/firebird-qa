#coding:utf-8
#
# id:           functional.gtcs.isql_show_command_ambiguity
# title:        GTCS/tests/CF_ISQL_22. SHOW TABLE / VIEW: ambiguity between tables and views
# decription:   
#               	::: NB ::: 
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_22.script
#               
#                   bug #223513 ambiguity between tables and views
#               
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

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table t(a int);
    create view v as select a from t;
    show tables;
    show views;
    show table v;
    show table t;
    show view v;
    show view t;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    T
    V
    A INTEGER Nullable
    A INTEGER Nullable

    View Source:
    select a from t
  """
expected_stderr_1 = """
    There is no table V in this database
    There is no view T in this database
  """

@pytest.mark.version('>=2.5')
def test_isql_show_command_ambiguity_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

