#coding:utf-8

"""
ID:          issue-6495
ISSUE:       6495
TITLE:       UNIQUE / PRIMARY KEY constraint can be violated when AUTODDL = OFF and mixing commands for DDL and DML
DESCRIPTION:
JIRA:        CORE-6252
FBTEST:      bugs.core_6252
NOTES:
    [169.04.2026] pzotov
    Refactored (simplified code).
    Discussed with Alex and Vlad, adjusted output to the current one in FB 6.x
    (changed since shared metacache was introduced, 6.0.0.1771-f73321c 25.02.2026).
    Checked on 6.0.0.1891; 5.0.4.1808; 4.0.7.3269; 3.0.14.33855
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set autoddl off; -- [ !! ]
    commit;

    recreate table test1(
        a int not null,
        b int not null
    );
    commit;

    insert into test1(a, b) values (1,1);
    insert into test1(a, b) values (1,2);
    commit;

    -----------------------
    update test1 set b = 3;
    -----------------------

    set bail OFF;
    alter table test1 add constraint test1_unq unique (a);
    commit;

    rollback;

    set heading off;
    set count on;
    select * from test1;
    commit;

    -- We have to ensure that there are no indices that were created (before this bug fixed)
    -- for maintainace of PK/UNQ constraints:
    select
        ri.rdb$index_name idx_name
        ,ri.rdb$unique_flag idx_uniq
    from rdb$database r
    left join rdb$indices ri on
        ri.rdb$relation_name starting with 'TEST'
        and ri.rdb$system_flag is distinct from 1
    ;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)


@pytest.mark.version('>=3.0.6')
def test_1(act: Action):

    expected_stdout_5x = """
        Statement failed, SQLSTATE = 23000
        violation of PRIMARY or UNIQUE KEY constraint "TEST1_UNQ" on table "TEST1"
        -Problematic key value is ("A" = 1)

        1 1
        1 2
        Records affected: 2

        <null> <null>
        Records affected: 1
    """

    expected_stdout_6x = """
        Statement failed, SQLSTATE = 23000
        unsuccessful metadata update
        -ALTER TABLE "PUBLIC"."TEST1" failed
        -violation of PRIMARY or UNIQUE KEY constraint "TEST1_UNQ" on table "PUBLIC"."TEST1"
        -Problematic key value is ("A" = 1)

        1 3
        1 3
        Records affected: 2

        <null> <null>
        Records affected: 1
    """
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
