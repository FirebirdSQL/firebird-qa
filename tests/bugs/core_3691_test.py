#coding:utf-8

"""
ID:          issue-4039
ISSUE:       4039
TITLE:       Missing constraint name in foreign key error message in FB 2.1.4
DESCRIPTION:
JIRA:        CORE-3691
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    --  Note. Info about problematic key exists since 2.5.3
    recreate table tmain(id int primary key using index tmain_pk);
    commit;
    insert into tmain values(1);
    commit;
    recreate table tdetl(id int primary key using index tdetl_pk, pid int);
    commit;
    insert into tdetl values(1,2);
    commit;
    alter table tdetl add constraint tdetl_fk foreign key(pid) references tmain(id);
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "TDETL_FK" on table "TDETL"
    -Foreign key reference target does not exist
    -Problematic key value is ("PID" = 2)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

