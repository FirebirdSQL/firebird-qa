#coding:utf-8
#
# id:           bugs.core_2359
# title:        Logical multibyte maximum string length is not respected when assigning numbers
# decription:   
# tracker_id:   CORE-2359
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t (c varchar(2) character set utf8);

"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """insert into t values ('aaaaaaaa'); -- error: ok
insert into t values (12345678); -- pass: not ok
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 22001
arithmetic exception, numeric overflow, or string truncation
-string right truncation
-expected length 2, actual 8
Statement failed, SQLSTATE = 22001
arithmetic exception, numeric overflow, or string truncation
-string right truncation
-expected length 2, actual 8
"""

@pytest.mark.version('>=3.0')
def test_core_2359_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

