#coding:utf-8

"""
ID:          issue-3979
ISSUE:       3979
TITLE:       Server crashes with access violation when inserting row into table with unique index
DESCRIPTION:
JIRA:        CORE-3627
FBTEST:      bugs.core_3627
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- Confirmed crash on WI-V2.5.1.26351:
    -- Statement failed, SQLSTATE = 08006
    -- Unable to complete network request to host "localhost".
    -- -Error reading data from the connection.

    recreate table testtable
    (
      "ID" integer not null,
      "CLASSID" integer,
      primary key ("ID")
    );
    insert into TestTable values(1, 1);
    insert into TestTable values(2, 2);
    commit;

    alter table testtable add ksgfk integer;
    create unique index classidksgidx on testtable (classid, ksgfk);

    insert into testtable values(3,1,null);
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    attempt to store duplicate value (visible to active transactions) in unique index "CLASSIDKSGIDX"
    -Problematic key value is ("CLASSID" = 1, "KSGFK" = NULL)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

