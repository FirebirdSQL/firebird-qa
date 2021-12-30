#coding:utf-8
#
# id:           bugs.core_6987
# title:        DATEDIFF does not support fractional value for MILLISECOND
# decription:   
#                   Checked on 5.0.0.240; 4.0.1.2621; 3.0.8.33506.
#                
# tracker_id:   CORE-6987
# min_versions: []
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = [('^((?!sqltype:|DD_).)*$', ''), ('[ \t]+', ' '), ('.*alias:.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set list on;

    select datediff(millisecond from timestamp '0001-01-01' to timestamp '0001-01-01 00:00:00.0001') dd_01 from rdb$database;
    select datediff(millisecond from timestamp '9999-12-31 23:59:59.9999' to timestamp '0001-01-01 00:00:00.0001') dd_02 from rdb$database;

    select datediff(millisecond from time '00:00:00' to time '00:00:00.0001') dd_03 from rdb$database;
    select datediff(millisecond from time '23:59:59' to time '00:00:00.0001') dd_04 from rdb$database;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 580 INT64 scale: -1 subtype: 0 len: 8
    : name: DATEDIFF alias: DD_01
    : table: owner:
    DD_01 0.1

    01: sqltype: 580 INT64 scale: -1 subtype: 0 len: 8
    : name: DATEDIFF alias: DD_02

    DD_02 -315537897599999.8

    01: sqltype: 580 INT64 scale: -1 subtype: 0 len: 8
    : name: DATEDIFF alias: DD_03
    DD_03 0.1

    01: sqltype: 580 INT64 scale: -1 subtype: 0 len: 8
    : name: DATEDIFF alias: DD_04
    DD_04 -86398999.9
"""

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

