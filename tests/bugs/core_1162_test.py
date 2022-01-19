#coding:utf-8

"""
ID:          issue-1585
ISSUE:       1585
TITLE:       Problem altering numeric field type
DESCRIPTION:
  create table tab (a numeric(4,2));
  insert into tab values (99.99);
  select * from tab;

  A
  =======
    99.99

  alter table tab alter a type numeric(4,3);
  select * from tab;

  Statement failed, SQLCODE = -802
  arithmetic exception, numeric overflow, or string truncation

  BTW the database is not "corrupted" too badly - you can revert the change back by
  alter table tab alter a type numeric(4,2);
  and the engine is clever enough to convert data from stored format to requested one
  directly, not through all intermediate format versions.
JIRA:        CORE-1162
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """create table tab ( a numeric(4,2) );
insert into tab values (99.99);
alter table tab alter a type numeric(4,3);
select * from tab;
"""

act = isql_act('db', test_script)

expected_stdout = """A
=======
  99.99

"""

expected_stderr = """Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER TABLE TAB failed
-New scale specified for column A must be at most 2.
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

