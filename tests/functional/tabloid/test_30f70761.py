#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/30f707611aeed904c081c442192f0b6a5850501d
TITLE:       Check every foreign key referencing a primary/unique key on parent delete or key update
DESCRIPTION:
    Investigation of the problem that was solved by commit and test prototype have been done by zcode.ai.
    The regression was introduced by #df78ac84 (25.07.2025, "Small optimization when checking foreign keys").
    After that, it was possible to delete or update record in master table *after* failed similar DML and
    make some record in one of child tables to become orphan.
NOTES:
    [14.10.2026] pzotov
    It is enough to check only 6x+, previous major versions not affected.
    Expected output for 5x was added here in order to have ability to compare results.

    Confirmed bug on 6.0.0.2210-a3f935f.
    Checked on 6.0.0.2211-30f7076.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    create table t_main (
        id int constraint pk_parent primary key
    );

    create table t_detl1 (
        id int constraint pk_t_detl1 primary key,
        pid int constraint fk_t_detl1 references t_main(id)
    );

    create table t_detl2 (
        id int constraint pk_t_detl2 primary key,
        pid int constraint fk_t_detl2 references t_main(id)
    );

    set term ^;
    create procedure show_data (
        a_title_msg varchar(30)
    ) returns (
        table_name varchar(30), id int, pid int
    ) as
    begin
        for
            select :a_title_msg as tbl, id, cast(null as int) as pid from t_main
            UNION ALL
            select 't_detl1', id, pid from t_detl1
            UNION ALL
            select 't_detl2', id, pid from t_detl2
            order by 1,2,3
        into
            table_name, id, pid
        do
            suspend;
    end
    ^ set term ;^
    commit;

    insert into t_main(id) values (1);
    insert into t_main(id) values (2);
    insert into t_main(id) values (3);
    insert into t_main(id) values (4);

    -- t_main row 1 is referenced only by t_detl1
    insert into t_detl1 values (11, 1);

    -- t_main row 2 is referenced only by t_detl2
    insert into t_detl2 values (22, 2);

    -- t_main row 3 is referenced by both t_detl*
    insert into t_detl1 values (13, 3);
    insert into t_detl2 values (23, 3);

    -- t_main row 4 is referenced by t_detl2
    insert into t_detl2 values (24, 4);
    commit;

    --select * from show_data('original-tmain');

    set bail OFF;

    -- #########################
    -- ###  1.  D E L E T E  ###
    -- #########################
    -- test 1.1: delete t_main row referenced only by t_detl1 (first fk)
    -- Expected: fk violation. Actual before fix: the same.
    delete from t_main where id = 1;

    -- test 1.2: delete t_main row referenced only by t_detl2 (second fk)
    -- Expected: fk violation. Actual before fix: passed (bug)
    delete from t_main where id = 2;

    -- test 1.3: delete t_main row referenced by both t_detl*
    -- Expected: fk violation. Actual before fix: the same.
    delete from t_main where id = 3;

    ---------------------------------------------------------------
    -- what survived ?
    select * from show_data('after-delete t_main');

    rollback;


    -- #########################
    -- ###  2.  U P D A T E  ###
    -- #########################
    -- 2.1 try to renumber t_main key 3 -> 33
    -- Expected: fk violation. Actual before fix: the same.
    update t_main set id = 33 where id = 3;

    -- 2.2 try to renumber t_main key 4 -> 44
    -- Expected: fk violation. Actual before fix: passed (bug)
    update t_main set id = 44 where id = 4;

    select * from show_data('after-update t_main');
"""

substitutions = [] # [('[ \t]+', ' '), ('===.*', '')]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.ai
@pytest.mark.version('>=6.0')
def test_1(act: Action):
    expected_stdout_5x = """
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL1" on table "T_DETL1"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 1)
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL2" on table "T_DETL2"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 2)
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL1" on table "T_DETL1"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 3)
        TABLE_NAME                               ID          PID
        ============================== ============ ============
        after-delete t_main                       1       <null>
        after-delete t_main                       2       <null>
        after-delete t_main                       3       <null>
        after-delete t_main                       4       <null>
        t_detl1                                  11            1
        t_detl1                                  13            3
        t_detl2                                  22            2
        t_detl2                                  23            3
        t_detl2                                  24            4
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL1" on table "T_DETL1"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 3)
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL2" on table "T_DETL2"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 4)
        TABLE_NAME                               ID          PID
        ============================== ============ ============
        after-update t_main                       1       <null>
        after-update t_main                       2       <null>
        after-update t_main                       3       <null>
        after-update t_main                       4       <null>
        t_detl1                                  11            1
        t_detl1                                  13            3
        t_detl2                                  22            2
        t_detl2                                  23            3
        t_detl2                                  24            4
    """

    expected_stdout_6x = """
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL1" on table "PUBLIC"."T_DETL1"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 1)
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL2" on table "PUBLIC"."T_DETL2"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 2)
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL1" on table "PUBLIC"."T_DETL1"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 3)
        TABLE_NAME                               ID          PID
        ============================== ============ ============
        after-delete t_main                       1       <null>
        after-delete t_main                       2       <null>
        after-delete t_main                       3       <null>
        after-delete t_main                       4       <null>
        t_detl1                                  11            1
        t_detl1                                  13            3
        t_detl2                                  22            2
        t_detl2                                  23            3
        t_detl2                                  24            4
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL1" on table "PUBLIC"."T_DETL1"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 3)
        Statement failed, SQLSTATE = 23000
        violation of FOREIGN KEY constraint "FK_T_DETL2" on table "PUBLIC"."T_DETL2"
        -Foreign key references are present for the record
        -Problematic key value is ("ID" = 4)
        TABLE_NAME                               ID          PID
        ============================== ============ ============
        after-update t_main                       1       <null>
        after-update t_main                       2       <null>
        after-update t_main                       3       <null>
        after-update t_main                       4       <null>
        t_detl1                                  11            1
        t_detl1                                  13            3
        t_detl2                                  22            2
        t_detl2                                  23            3
        t_detl2                                  24            4
    """
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
