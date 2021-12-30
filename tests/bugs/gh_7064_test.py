#coding:utf-8
#
# id:           bugs.gh_7064
# title:        Linear regression functions aren't implemented correctly
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/7064
#               
#                   Confirmed bug on 5.0.0.336 (Windows only), 4.0.1.2672 (both Windows and Linux).
#                   Results were: 5.538881418962480e-316; 8.320318437577263e-317;  6.902055141081681e-310
#                   Checked on: 5.0.0.338, 4.0.1.2682 - all fine.
#                
# tracker_id:   
# min_versions: ['4.0.1']
# versions:     4.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select regr_avgx(a, b)
    from (
      select 1, 1 from RDB$DATABASE union all
      select 2, 1 from RDB$DATABASE union all
      select 3, 2 from RDB$DATABASE union all
      select 4, 2 from RDB$DATABASE
    ) t (a, b);

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1.500000000000000
"""

@pytest.mark.version('>=4.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
