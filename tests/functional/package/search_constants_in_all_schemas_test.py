#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/812413420e110cb77cdd9688b888f5e1ff9e3d1e
TITLE:       Search existing package constants in all SCHEMAs
DESCRIPTION:
NOTES:
    [05.07.2026] pzotov
    Source question and additional explanations (thanks to Artyom Abakumov)
        https://groups.google.com/g/firebird-devel/c/RhAZUvc5J24/m/Dd2tHGptAQAJ
        https://groups.google.com/g/firebird-devel/c/RhAZUvc5J24/m/50lY3X7mAQAJ
    Confirmed issues on 6.0.0.1948-f8eee95.
    Checked on 6.0.0.2062-f9055bf.
"""

import pytest
from firebird.qa import *

db = db_factory()
substitutions = [('[ \t]+', ' '), ('CONST_SRC_BLOB_ID.*', '')]
act = python_act('db', substitutions = substitutions)
tmp_user = user_factory('db', name = 'tmp_package_const_user', password ='123')

CONST_NAME_EXAMPLE = 'phone'.upper()
CONST_VAL_EXAMPLE = '+33620022222'

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_user: User):

    test_sql = f"""
        set blob all;
        set list on;
        set autoddl off;
        set autoterm on;

        create schema stock;
        create package stock.pg_test as
        begin
            constant {CONST_NAME_EXAMPLE} varchar(12) = '{CONST_VAL_EXAMPLE}';
        end
        ;

        -- check #1:
        -- "Add constant missing RDB$CONSTANT_SOURCE setup"
        -- (explanation: RDB$CONSTANT_SOURCE value was missing for user made package constants)
        select k.rdb$constant_name as const_name, k.rdb$constant_source as const_src_blob_id
        from rdb$constants k where k.rdb$schema_name = upper('stock') and k.rdb$package_name = upper('pg_test')
        ;

        -- check #2:
        -- "Search existing package constants in all SCHEMAs"
        -- (explanation: first existing schema from the schema search list was taken, not the first schema containing constant in question)
        set search_path to public, stock;
        select pg_test.{CONST_NAME_EXAMPLE} as phone from rdb$database;

        commit;

        -- ##################################################################################
        -- check #3:
        -- "Store EXECUTE privilege for all SYSTEM packages"
        -- (explanation: Execute permissions are checked only when quering a *CONSTANT* from a system package)
        -- Make connection as NON-privileged user:

        connect '{act.db.dsn}' user {tmp_user.name} password '{tmp_user.password}';
        execute block returns (all_sys_constants_not_null smallint) as
        begin
            for
                select
                    system.rdb$blob_util.from_begin as sys_const_from_begin
                    ,system.rdb$blob_util.from_current as sys_const_from_current
                    ,system.rdb$blob_util.from_end as sys_const_from_end
                from rdb$database
                as cursor c
            do begin
                all_sys_constants_not_null = abs(sign(c.sys_const_from_begin + c.sys_const_from_current + c.sys_const_from_end));
                suspend;
            end
        end;
    """

    act.expected_stdout = f"""
        CONST_NAME                      {CONST_NAME_EXAMPLE}
        = '{CONST_VAL_EXAMPLE}'
        {CONST_NAME_EXAMPLE}            {CONST_VAL_EXAMPLE}
        ALL_SYS_CONSTANTS_NOT_NULL      1
    """
    act.isql(switches = ['-q'], input = test_sql, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
