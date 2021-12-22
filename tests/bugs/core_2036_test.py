#coding:utf-8
#
# id:           bugs.core_2036
# title:        Parameters order of EXECUTE BLOCK statement is reversed if called from EXECUTE STATEMENT
# decription:   
#                   2.5.9.27107: OK, 0.328s.
#                   3.0.4.32924: OK, 0.906s.
#                   4.0.0.918: OK, 1.110s.
#                 
# tracker_id:   CORE-2036
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    execute block returns(p1 int, p2 int, p3 int) as
        declare s varchar(255);
    begin
        s =    'execute block ( i1 int = ?, i2 int = ?, i3 int = ? ) returns(o1 int, o2 int, o3 int) as '
            || 'begin '
            || '    o1 = i1 * 2; '
            || '    o2 = i2 * 4; '
            || '    o3 = i3 * 8; '
            || '    suspend; '
            || 'end '
        ;
        execute statement (s) (654, 543, 432) into p1, p2, p3;
        suspend;
    end
    ^
    set term ^;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    P1                              1308
    P2                              2172
    P3                              3456
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

