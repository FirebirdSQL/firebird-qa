#coding:utf-8
#
# id:           bugs.core_0870
# title:        Engine crashes while trying to backup a logically corrupt db
# decription:   This test works only for fb 2.1-2.5 and was converted to dummy one for 3.0 as it needs specificaly corrupted database. We don't have such database with ODS 12 required by fb 3.0+
# tracker_id:   CORE-870
# min_versions: ['2.1']
# versions:     3.0
# qmid:         bugs.core_870

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on; select 'Extracted .fdb file has not supported ODS for using on Firebird 3.0' as msg from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             Extracted .fdb file has not supported ODS for using on Firebird 3.0
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

