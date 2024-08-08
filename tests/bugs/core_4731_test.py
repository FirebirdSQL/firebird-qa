#coding:utf-8

"""
ID:          issue-5037
ISSUE:       5037
TITLE:       Prohibit an ability to issue DML or DDL statements on RDB$ tables
DESCRIPTION:
  Integral test for verifying ability to change system tables by non-privileged user and by those
  who have been granted with RDB$ADMIN role.
  Main idea: read system tables (hereafter - 'ST') metadata and generate all possible DML and DDL
  statements that are intended to:
  a) restrict ST by creating new table with foreign key to selected ST (if it has PK or UK);
  b) change data by issuing INSERT /  UPDATE / DELETE statements; also try SELECT ... WITH LOCK;
  c) change metadata: add column, alter column (drop NULL constraint, add new contraint, add DEFAULT value),
                      drop column;
  d) aux. actions: attempt to drop ST.
     *** 11-apr-2018: EXCLUDED attempt to create  index on ST: now it is allowed, see CORE-5746 ***
  e) make indirect changes: apply ALTER SEQUENCE statement for system generators

  Test contains following statements and procedures:
  1) creating two users, one of them is granted with role RDB$ADMIN.
     Both these users are granted to create/alter/drop any kinds of database objects.
  2) creating several user objects (domain, exception, collation, sequence, master/detail tables, trigger,
     view, stanalone procedure and standalone function and package). These objects are created in order
     to add some data in system tables that can be later actually affected by vulnerable expressions;
  3) proc sp_gen_expr_for_creating_fkeys:
     reads definition of every system table and if it has PK/UK than generate expressions for item "a":
     they will create completely new table with set of fields which id appropriate to build FOREIGN KEY
     to selected ST. Generated expressions are added to special table `vulnerable_on_sys_tables`;
  4) proc sp_gen_expr_for_direct_change:
     reads definition of every system table and generates DML and DDL expressions for items "b" ... "e" described
     in the previous section. These expressions are also added to table `vulnerable_on_sys_tables`;
  5) proc sp_run_vulnerable_expressions:
     reads expressions from table `vulnerable_on_sys_tables` and tries to run each of them via ES/EDS with user
     and role that are passed as input arguments. If expression raises exception than this SP will log its gdscode
     in WHEN ANY block and expression then is suppressed.
     If expression PASSES successfully than this SP *also* will log this event.
  6) two calls of sp_run_vulnerable_expressions: one for non-privileged user and second for user with role RDB$ADMIN.
  7) select values of raised gdscodes (distinct) in order to check that only ONE gdscode occured (335544926).
  8) select expressions that were PASSED without exceptions.
NOTES:
    [18.02.2020] pzotov
        REFACTORED: most of initial code was moved into $files_location/core_4731.sql; changed test_type to 'Python'.
    [04.03.2023] pzotov
        Separated code for FB-4x because it allows now statement 'delete from RDB$BACKUP_HISTORY ...'
        Checked on 5.0.0.970, 4.0.3.2904, 3.0.11.33665.
    [08.08.2024] pzotov
        Separated code for FB-6x because it became differ after implemented GH-8202
        https://github.com/FirebirdSQL/firebird/commit/0cc8de396a3c2bbe13b161ecbfffa8055e7b4929
        (05-aug-2024 13:45, "Regenerate system triggers improving formatting and constant names")
        Checked on 6.0.0.419-3505a5e
JIRA:        CORE-4731
FBTEST:      bugs.core_4731
"""

import pytest
import time
from pathlib import Path
from firebird.qa import *
from firebird.driver import ShutdownMode, ShutdownMethod

db = db_factory()

dba_privileged_user = user_factory('db', name='tmp_c4731_cooldba', password='123')
non_privileged_user = user_factory('db', name='tmp_c4731_manager', password='123')

act = python_act('db')

fb3x_expected_out = """
    -- Executed with role: NONE. Expressions that passes WITHOUT errors:
    -- count_of_passed:             0
    -- gdscode list for blocked:    335544926

    -- Executed with role: RDB$ADMIN. Expressions that passes WITHOUT errors:
    -- count_of_passed:             23
    VULNERABLE_EXPR                 insert into RDB$BACKUP_HISTORY(RDB$BACKUP_ID , RDB$TIMESTAMP , RDB$BACKUP_LEVEL , RDB$GUID , RDB$SCN , RDB$FILE_NAME) values(null, null, null, null, null, null) returning rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 delete from RDB$DB_CREATORS t  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 insert into RDB$DB_CREATORS(RDB$USER , RDB$USER_TYPE) values(null, null) returning rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER = 'C'  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER = null  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER_TYPE = 32767  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER_TYPE = null  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$FUNCTIONS t  set t.RDB$FUNCTION_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PACKAGES t  set t.RDB$PACKAGE_BODY_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PACKAGES t  set t.RDB$PACKAGE_HEADER_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PROCEDURES t  set t.RDB$PROCEDURE_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$RELATIONS t  set t.RDB$VIEW_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TRIGGERS t  set t.RDB$TRIGGER_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 insert into RDB$TYPES(RDB$FIELD_NAME , RDB$TYPE , RDB$TYPE_NAME , RDB$DESCRIPTION , RDB$SYSTEM_FLAG) values(null, null, null, null, null) returning rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$DESCRIPTION = 'test_for_blob' where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$DESCRIPTION = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$FIELD_NAME = 'C' where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$FIELD_NAME = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$SYSTEM_FLAG = 32767 where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$TYPE = 32767 where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$TYPE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$TYPE_NAME = 'C' where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$TYPE_NAME = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    -- gdscode list for blocked:    335544926
"""

fb4x_expected_out = """
    -- Executed with role: NONE. Expressions that passes WITHOUT errors:
    -- count_of_passed:             0
    -- gdscode list for blocked:    335544926

    -- Executed with role: RDB$ADMIN. Expressions that passes WITHOUT errors:
    -- count_of_passed:             24
    VULNERABLE_EXPR                 delete from RDB$BACKUP_HISTORY t  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 insert into RDB$BACKUP_HISTORY(RDB$BACKUP_ID , RDB$TIMESTAMP , RDB$BACKUP_LEVEL , RDB$GUID , RDB$SCN , RDB$FILE_NAME) values(null, null, null, null, null, null) returning rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 delete from RDB$DB_CREATORS t  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 insert into RDB$DB_CREATORS(RDB$USER , RDB$USER_TYPE) values(null, null) returning rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER = 'C'  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER = null  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER_TYPE = 32767  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER_TYPE = null  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$FUNCTIONS t  set t.RDB$FUNCTION_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PACKAGES t  set t.RDB$PACKAGE_BODY_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PACKAGES t  set t.RDB$PACKAGE_HEADER_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PROCEDURES t  set t.RDB$PROCEDURE_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$RELATIONS t  set t.RDB$VIEW_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TRIGGERS t  set t.RDB$TRIGGER_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 insert into RDB$TYPES(RDB$FIELD_NAME , RDB$TYPE , RDB$TYPE_NAME , RDB$DESCRIPTION , RDB$SYSTEM_FLAG) values(null, null, null, null, null) returning rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$DESCRIPTION = 'test_for_blob' where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$DESCRIPTION = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$FIELD_NAME = 'C' where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$FIELD_NAME = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$SYSTEM_FLAG = 32767 where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$TYPE = 32767 where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$TYPE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$TYPE_NAME = 'C' where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TYPES t  set t.RDB$TYPE_NAME = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    -- gdscode list for blocked:    335544926
"""

fb6x_expected_out = """
    -- Executed with role: NONE. Expressions that passes WITHOUT errors:
    -- count_of_passed:             0
    -- gdscode list for blocked:    335544926
    -- Executed with role: RDB$ADMIN. Expressions that passes WITHOUT errors:
    -- count_of_passed:             14
    VULNERABLE_EXPR                 delete from RDB$BACKUP_HISTORY t  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 insert into RDB$BACKUP_HISTORY(RDB$BACKUP_ID , RDB$TIMESTAMP , RDB$BACKUP_LEVEL , RDB$GUID , RDB$SCN , RDB$FILE_NAME) values(null, null, null, null, null, null) returning rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 delete from RDB$DB_CREATORS t  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 insert into RDB$DB_CREATORS(RDB$USER , RDB$USER_TYPE) values(null, null) returning rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER = 'C'  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER = null  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER_TYPE = 32767  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$DB_CREATORS t  set t.RDB$USER_TYPE = null  rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$FUNCTIONS t  set t.RDB$FUNCTION_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PACKAGES t  set t.RDB$PACKAGE_BODY_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PACKAGES t  set t.RDB$PACKAGE_HEADER_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$PROCEDURES t  set t.RDB$PROCEDURE_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$RELATIONS t  set t.RDB$VIEW_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    VULNERABLE_EXPR                 update RDB$TRIGGERS t  set t.RDB$TRIGGER_SOURCE = null where coalesce(rdb$system_flag,0)=0 rows 1 returning t.rdb$db_key; -- length of returned rdb$dbkey=8
    -- gdscode list for blocked:    335544926

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, dba_privileged_user: User, non_privileged_user: User, capsys):
    # Run prepare script
    prep_script = (act.files_dir / 'core_4731.sql').read_text()
    prep_script = prep_script % {'dba_privileged_name': dba_privileged_user.name,
                                 'non_privileged_name': non_privileged_user.name}
    act.isql(switches=['-q'], input=prep_script, combine_output = True)
    assert act.clean_stdout == ''
    act.reset()

    # Remove all attachments that can stay alive after preparing DB because of ExtConnPoolLifeTime > 0:
    with act.connect_server() as srv:
        srv.database.shutdown(database=act.db.db_path, mode=ShutdownMode.FULL,
                              method=ShutdownMethod.FORCED, timeout=0)
        srv.database.bring_online(database=act.db.db_path)
    #
    test_script = f"""
        -- ###################################################################################
        --                 R U N    A S   N O N - P R I V I L E G E D    U S E R
        -- ###################################################################################
        execute procedure sp_run_vulnerable_expressions('{non_privileged_user.name}', '123', 'NONE');

        -- Note: as of build 3.0.31810, we can SKIP restoring of 'pure-state' of RDB$ tables
        -- after this SP because non-privileged user can NOT change enything.
        -- All his attempts should FAIL, system tables should be in unchanged state.

        set list off;
        set heading off;

        select '-- Executed with role: '||trim(( select actual_role from vulnerable_on_sys_tables rows 1 ))
                   ||'. Expressions that passes WITHOUT errors:' as msg
        from rdb$database
        ;

        commit; -- 11-04-2018, do not remove!
        set transaction no wait;

        set list on;
        select count(*) as "-- count_of_passed: "
        from v_passed;

        set list on;
        select * from v_passed;

        set list on;
        select distinct vulnerable_gdscode as "-- gdscode list for blocked:"
        from vulnerable_on_sys_tables
        where vulnerable_gdscode is distinct from -1;

        -- #########################################################################################
        -- R U N    A S   U S E R    W H O    I S    G R A N T E D     W I T H     R B D $ A D M I N
        -- #########################################################################################
        execute procedure sp_run_vulnerable_expressions('{dba_privileged_user.name}', '123', 'RDB$ADMIN');

        set list off;
        set heading off;

        select '-- Executed with role: '||trim(( select actual_role from vulnerable_on_sys_tables rows 1 ))
                   ||'. Expressions that passes WITHOUT errors:' as msg
        from rdb$database
        ;
        commit; -- 11-04-2018, do not remove!

        set list on;
        select count(*) as "-- count_of_passed: "
        from v_passed;

        set list on;
        select * from v_passed;

        set list on;
        select distinct vulnerable_gdscode as "-- gdscode list for blocked:"
        from vulnerable_on_sys_tables
        where vulnerable_gdscode is distinct from -1;

        ----------------
        commit;

        connect '{act.db.dsn}' user '{act.db.user}' password '{act.db.password}';

        --                                    ||||||||||||||||||||||||||||
        -- ###################################|||  FB 4.0+, SS and SC  |||##############################
        --                                    ||||||||||||||||||||||||||||
        -- If we check SS or SC and ExtConnPoolLifeTime > 0 (config parameter FB 4.0+) then current
        -- DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
        -- will not able to drop this database at the final point of test.
        -- Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
        -- we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
        -- in the letter to hvlad and dimitr 13.10.2019 11:10).
        -- This means that one need to kill all connections to prevent from exception on cleanup phase:
        -- SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
        -- #############################################################################################
        delete from mon$attachments where mon$attachment_id != current_connection;
        commit;
    """
    
    act.expected_stdout = fb3x_expected_out if act.is_version('<4') else fb4x_expected_out if act.is_version('<6') else fb6x_expected_out
    act.isql(switches=['-q'], input=test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
