#coding:utf-8
#
# id:           bugs.core_6109
# title:        Changing FLOAT to a SQL standard compliant FLOAT datatype
# decription:   
#                   Checked on 4.0.0.1763 SS: 1.453s.
#                
# tracker_id:   CORE-6109
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!(sqltype)).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(
       r real
      ,f float
      ,f01 float( 1)
      ,f24 float(24)
      ,f25 float(25)
      ,f53 float(53)
    );

    set list on;
    set sqlda_display on;
    select * from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 482 FLOAT Nullable scale: 0 subtype: 0 len: 4
    02: sqltype: 482 FLOAT Nullable scale: 0 subtype: 0 len: 4
    03: sqltype: 482 FLOAT Nullable scale: 0 subtype: 0 len: 4
    04: sqltype: 482 FLOAT Nullable scale: 0 subtype: 0 len: 4
    05: sqltype: 480 DOUBLE Nullable scale: 0 subtype: 0 len: 8
    06: sqltype: 480 DOUBLE Nullable scale: 0 subtype: 0 len: 8
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

