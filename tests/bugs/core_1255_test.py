#coding:utf-8
#
# id:           bugs.core_1255
# title:        String truncation error when concatenating _UTF8 string onto extract(year result
# decription:   The query
#               
#               SELECT ((EXTRACT(YEAR FROM CAST('2007-01-01' AS DATE)) || _UTF8'')) col FROM rdb$database GROUP BY 1;
#               
#               Produces the error
#               Statement failed, SQLCODE = -802
#               arithmetic exception, numeric overflow, or string truncation
# tracker_id:   CORE-1255
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1255

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT ((EXTRACT(YEAR FROM CAST('2007-01-01' AS DATE)) || _UTF8'')) col FROM rdb$database GROUP BY 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """COL
======
2007

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

