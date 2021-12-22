#coding:utf-8
#
# id:           bugs.core_1712
# title:        Buffer overflow in conversion
# decription:   
#                 Confirmed bug on WI-V2.0.0.12724:
#                     * "buffer overrun" when use dialect 1;
#                     * "string right truncation" when use dialect 3.
#                  Checked on:
#                      Windows: 3.0.8.33445, 4.0.0.2416
#                      Linux:   3.0.8.33426, 4.0.0.2416
#                
# tracker_id:   CORE-1712
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """
    recreate table testtable(f1 numeric(15, 2));
    commit;
    
    insert into testtable(f1) values(1e19);
    commit;
    
    set list on;
    select replace(cast(f1 as varchar(30)),'0','') f1_as_varchar30 from testtable;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F1_AS_VARCHAR30                 1.e+19
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

