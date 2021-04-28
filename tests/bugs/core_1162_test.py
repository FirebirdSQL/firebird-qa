#coding:utf-8
#
# id:           bugs.core_1162
# title:        Problem altering numeric field type
# decription:   create table tab ( a numeric(4,2) );
#               
#               insert into tab values (99.99);
#               
#               select * from tab;
#               
#               A
#               =======
#                 99.99
#               
#               alter table tab alter a type numeric(4,3);
#               
#               select * from tab;
#               
#               Statement failed, SQLCODE = -802
#               arithmetic exception, numeric overflow, or string truncation
#               
#               Btw. the database is not "corrupted" too badly - you can revert the change back by alter table tab alter a type numeric(4,2);
#               and the engine is clever enough to convert data from stored format to requested one directly, not through all intermediate format versions.
# tracker_id:   CORE-1162
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1162-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create table tab ( a numeric(4,2) );
insert into tab values (99.99);
alter table tab alter a type numeric(4,3);
select * from tab;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """A
=======
  99.99

"""
expected_stderr_1 = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER TABLE TAB failed
-New scale specified for column A must be at most 2.
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

