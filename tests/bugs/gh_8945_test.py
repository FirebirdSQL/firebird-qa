#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8945
TITLE:       ALTER COLUMN <BOOL_COL> TYPE [VAR]CHAR must be allowed
DESCRIPTION:
    Test create domain of boolean type and table with two boolean columns, with adding several rows in it.
    Then we alter domain from boolean to varchar and this must be allowed since fix.
    After this we alter type of boolean columns in the table:
        * first column is altered using direct specification of new data type, i.e. to 'varchar(5);
        * second column is altered via specification of domain type (and it is now also textual);
    No errors must occur during these steps.
    Finally, we query table and show types of returned boolean columns (using SQLDA_DISPLAY).
NOTES:
    [15.03.2026] pzotov
    Confirmed problem on 6.0.0.1816-0-0c91d1a.
    Checked on: 6.0.0.1824-0-00c4ad4.
"""
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    create domain dm_bool boolean;
    alter domain dm_bool type varchar(5);

    recreate table t_boolean_storage(id int primary key, val1 boolean, val2 boolean);
    insert into t_boolean_storage(id, val1, val2) select i, b, b from (select i, iif(mod(i,3)=2, null, mod(i,2) = 0) as b from ( select row_number()over() i from rdb$types rows 5));
    commit;
    -- Question remains.
    -- create index t_boolean_storage_val on t_boolean_storage(val1);
    -- commit;
    set sqlda_display on;

    alter table t_boolean_storage alter val1 type char(5);
    commit;
    select id as id, val1 as val_type_directly_spec from t_boolean_storage order by id;

    alter table t_boolean_storage alter val2 type dm_bool;
    commit;
    select id as id, val2 as val_type_from_domain_ddl from t_boolean_storage order by id;
"""

substitutions = [('[ \t]+', ' '), ('^((?!SQLSTATE|sqltype:|ID \\d+|VAL_TYPE_).)*$', ''), ]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    expected_stdout = """
        01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
        02: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 5 charset: 0 SYSTEM.NONE
        : name: VAL1 alias: VAL_TYPE_DIRECTLY_SPEC
        ID 1
        VAL_TYPE_DIRECTLY_SPEC FALSE
        ID 2
        VAL_TYPE_DIRECTLY_SPEC <null>
        ID 3
        VAL_TYPE_DIRECTLY_SPEC FALSE
        ID 4
        VAL_TYPE_DIRECTLY_SPEC TRUE
        ID 5
        VAL_TYPE_DIRECTLY_SPEC <null>

        01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
        02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 5 charset: 0 SYSTEM.NONE
        : name: VAL2 alias: VAL_TYPE_FROM_DOMAIN_DDL
        ID 1
        VAL_TYPE_FROM_DOMAIN_DDL FALSE
        ID 2
        VAL_TYPE_FROM_DOMAIN_DDL <null>
        ID 3
        VAL_TYPE_FROM_DOMAIN_DDL FALSE
        ID 4
        VAL_TYPE_FROM_DOMAIN_DDL TRUE
        ID 5
        VAL_TYPE_FROM_DOMAIN_DDL <null>
    """

    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
