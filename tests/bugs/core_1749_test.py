#coding:utf-8
#
# id:           bugs.core_1749
# title:        DDL statement with AUTODDL ON won't show statistics
# decription:   
# tracker_id:   CORE-1749
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('^Current memory.*', ''), ('^Delta memory.*', ''), ('^Max memory.*', ''), ('^Elapsed time.*', ''), ('^Buffers.*', ''), ('^Reads.*', ''), ('^Writes.*', ''), ('^Elapsed time.*', ''), ('^Cpu.*', ''), ('^Fetches.*', 'STATS')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set stat on;

create generator A;

set autoddl off;

create generator B;
commit;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """STATS
STATS
STATS
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

