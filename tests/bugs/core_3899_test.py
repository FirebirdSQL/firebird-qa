#coding:utf-8

"""
ID:          issue-4235
ISSUE:       4235
TITLE:       row_number(), rank() and dense_rank() return BIGINT datatype in dialect 1
DESCRIPTION:
JIRA:        CORE-3899
"""

import pytest
from firebird.qa import *

db = db_factory(sql_dialect=1)

test_script = """
    set sqlda_display on;
    set planonly;
    select row_number()over() rno, rank()over() rnk, dense_rank()over() drk
    from rdb$database;
    -- NB: on dialect-3 output is:
    -- sqltype: 580 INT64 ...
"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype:|name:).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')])

expected_stdout = """
    01: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
      :  name: ROW_NUMBER  alias: RNO
    02: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
      :  name: RANK  alias: RNK
    03: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
      :  name: DENSE_RANK  alias: DRK
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

