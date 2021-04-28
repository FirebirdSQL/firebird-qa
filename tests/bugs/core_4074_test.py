#coding:utf-8
#
# id:           bugs.core_4074
# title:        Computed by columns and position function
# decription:   
# tracker_id:   CORE-4074
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test01 (
      f01 computed by ( 'fabio ' || position('x','schunig') ),
      f02 numeric(8,2) default 0
    );
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    show table test01;
    -- ::: NB ::: On WI-V2.5.4.26856, 26-mar-2015, output is:
    -- F01                             Computed by: ( 'fabio ' || position('x','schunig') ),
    --   f02 numeric(8,2) default 0
    -- )
    -- F02                             NUMERIC(8, 2) Nullable )
    -- (i.e. it DOES contain "strange" last line)
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F01                             Computed by: ( 'fabio ' || position('x','schunig') )
    F02                             NUMERIC(8, 2) Nullable default 0
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

