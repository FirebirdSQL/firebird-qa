#coding:utf-8

"""
ID:          issue-4039
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/4039
TITLE:       Missing constraint name in foreign key error message in FB 2.1.4
DESCRIPTION:
JIRA:        CORE-3691
FBTEST:      bugs.core_3691
NOTES:
    [12.04.2026] pzotov
    Adjusted output in 6.x (changes caused by shared metadata cache intro, 25.02.2026).
    Checked on: 6.0.0.1891; 5.0.4.1808; 4.0.7.3269; 3.0.14.33855.
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

@pytest.mark.version('>=3')
def test_1(act: Action):

    expected_stdout_5x = f"""
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "TDETL_FK" on table "TDETL"
        -Foreign key reference target does not exist
        -Problematic key value is ("PID" = 2)
    """

    expected_stdout_6x = f"""
        Statement failed, SQLSTATE = 23000
        unsuccessful metadata update
        -ALTER TABLE "PUBLIC"."TDETL" failed
        -violation of FOREIGN KEY constraint "TDETL_FK" on table "PUBLIC"."TDETL"
        -Foreign key reference target does not exist
        -Problematic key value is ("PID" = 2)
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

