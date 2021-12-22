#coding:utf-8
#
# id:           bugs.core_3899
# title:        row_number(), rank() and dense_rank() return BIGINT datatype in dialect 1
# decription:   
# tracker_id:   CORE-3899
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype:|name:).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=1, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set planonly;
    select row_number()over() rno, rank()over() rnk, dense_rank()over() drk 
    from rdb$database;
    -- NB: on dialect-3 output is:
    -- sqltype: 580 INT64 ...
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
      :  name: ROW_NUMBER  alias: RNO
    02: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
      :  name: RANK  alias: RNK
    03: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
      :  name: DENSE_RANK  alias: DRK
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

