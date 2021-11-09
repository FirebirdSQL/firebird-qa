#coding:utf-8
#
# id:           bugs.core_6160
# title:        SUBSTRING of non-text/-blob is described to return NONE character set in DSQL
# decription:
#                   Confirmed output of: ' ... charset: 0 NONE' on 4.0.0.1627.
#                   Works as described in the ticket since 4.0.0.1632 ('... charset: 2 ASCII').
#                   NOTE. In the 'substitution' section we remove all rows except line with phrase 'charset' in it.
#                   Furter, we have to remove digital ID for this charset because it can be changed in the future:
#                   'charset: 2 ASCII' --> 'charset: ASCII'
#
# tracker_id:   CORE-6160
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!charset).)*$', ''), ('[ \t]+', ' '), ('.*charset: [\\d]+', 'charset:')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- 01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 1 charset: 2 ASCII
    set sqlda_display on;
    set planonly;
    select substring(1 from 1 for 1) from rdb$database;
    select substring(current_date from 1 for 1) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    charset: ASCII
    charset: ASCII
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.charset = 'NONE'
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

