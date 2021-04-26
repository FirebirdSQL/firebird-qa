#coding:utf-8
#
# id:           bugs.core_2355
# title:        Incorrect handling of LOWER/UPPER when result string shrinks in terms of byte length
# decription:   
# tracker_id:   CORE-2355
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT LOWER('İA') FROM RDB$DATABASE;
SELECT LOWER('AӴЁΪΣƓİ') FROM RDB$DATABASE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
LOWER
======
ia


LOWER
=======
aӵёϊσɠi

"""

@pytest.mark.version('>=3.0')
def test_core_2355_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

