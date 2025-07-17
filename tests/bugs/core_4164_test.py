#coding:utf-8

"""
ID:          issue-4491
ISSUE:       4491
TITLE:       Owner name is missing for generators/exceptions restored from a backup
DESCRIPTION:
JIRA:        CORE-4164
FBTEST:      bugs.core_4164
NOTES:
    [17.07.2025] pzotov
    Checked on 6.0.0.835; 5.0.3.1661; 4.0.6.3207; 3.0.13.33807.
"""

import pytest
from firebird.qa import *

init_script = """
    -- Scenario for this test:
    -- create sequence g;
    -- create exception e 'blablabla';
    -- commit;
    -- grant usage on sequence g to tmp$4164;
    -- grant usage on exception e to tmp$4164;
    -- grant usage on sequence g to mgr$4164 with grant option;
    -- grant usage on exception e to mgr$4164 with grant option;
    -- commit;
    -- ==> and then do backup.
"""

db = db_factory(from_backup='core4164.fbk')

act = isql_act('db', substitutions=[('=.*', '')])

@pytest.mark.version('>=3.0')
def test_1(act: Action):

    SQL_SCHEMA_PREFIX = '' if act.is_version('<6') else 'PUBLIC.'
    test_script = f"""
        set width usr 10;
        set width grantor 10;
        set width priv 4;
        set width with_grant 6;
        set width obj_name 10;
        set width fld_name 15;
        set count on;
        select
            p.rdb$user           usr
            ,p.rdb$grantor       grantor
            ,p.rdb$privilege     priv
             -- ::: NB ::: Field rdb$grant_option will contain NULLs after restoring,
             -- but <null> and 0 are considered by engine as the same in RDB$ tables.
             -- Decided to apply `coalesce` after consulting with Dmitry, letter 27.03.2015 19:26
            ,coalesce(p.rdb$grant_option, 0) with_grant
            ,p.rdb$relation_name obj_name
            ,p.rdb$user_type     usr_type
            ,p.rdb$object_type   obj_type
            ,p.rdb$field_name    fld_name
        from rdb$user_privileges p
        where upper(trim(p.rdb$relation_name)) in ( upper('g'), upper('e') )
        order by usr, grantor, obj_name, with_grant
        ;
    """

    expected_stdout = """
        USR        GRANTOR    PRIV   WITH_GRANT OBJ_NAME   USR_TYPE OBJ_TYPE FLD_NAME
        MGR$4164   SYSDBA     G               1 E                 8        7 <null>
        MGR$4164   SYSDBA     G               1 G                 8       14 <null>
        SYSDBA     SYSDBA     G               1 E                 8        7 <null>
        SYSDBA     SYSDBA     G               1 G                 8       14 <null>
        TMP$4164   SYSDBA     G               0 E                 8        7 <null>
        TMP$4164   SYSDBA     G               0 G                 8       14 <null>
        Records affected: 6
    """

    act.expected_stdout = expected_stdout
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

