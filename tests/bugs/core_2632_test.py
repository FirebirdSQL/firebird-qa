#coding:utf-8
#
# id:           bugs.core_2632
# title:        Invalid BLOB ID when working with monitoring tables
# decription:   
# tracker_id:   CORE-2632
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('SQL_TEXT_BLOB.*', 'SQL_TEXT_BLOB')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set blob all;
    select 1 as k from mon$database;
    set count on;

    select s.mon$sql_text as sql_text_blob 
    from mon$statements s
    where s.mon$sql_text NOT containing 'rdb$auth_mapping' -- added 30.03.2017 (4.0.0.x)
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    K                               1
    SQL_TEXT_BLOB
    select 1 as k from mon$database

    Records affected: 1
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

