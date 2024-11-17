#coding:utf-8

"""
ID:          issue-7675
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7675
TITLE:       EXPLAIN statement and RDB$SQL package
DESCRIPTION:
    Test only ckecks ability to use RDB$SQL package as it is described in the doc.
    More complex tests will be implemented later.
NOTES:
    [02.10.2023] pzotov
    Checked on 6.0.0.65.

    [17.11.2024] pzotov
    Removed output of concrete data for checked query.
    It is enough only to display content of SQLDA (lines with 'sqltype:' and 'name:') and SQLSTATE (if some error occurs).
    Checked on 6.0.0.532.
"""
import os

import pytest
from firebird.qa import *

init_sql = """
    recreate table tdetl(id int primary key);
    recreate table tmain(id int primary key using index tmain_pk, x int);
    recreate table tdetl(id int primary key using index tdetl_pk, pid int references tmain using index tdetl_fk, y int, z int);
    commit;

    insert into tmain(id,x) select row_number()over(), -100 + rand()*200 from rdb$types rows 100;
    insert into tdetl(id, pid, y,z) select row_number()over(), 1+rand()*99, rand()*1000, rand()*1000 from rdb$types;
    commit;

    create index tmain_x on tmain(x);
    create index tdetl_y on tdetl(y);
    create index tdetl_z on tdetl(z);

    set statistics index tdetl_fk;
    commit;
"""
db = db_factory(init = init_sql)

test_script = """
    set sqlda_display on;
    select p.*
    from rdb$sql.explain('select 1 from rdb$database') as p
    rows 0
    ;
"""

act = isql_act('db', test_script, substitutions=[('^((?!SQLSTATE|sqltype:|name:).)*$',''),('[ \t]+',' ')])

expected_stdout = """
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    : name: PLAN_LINE alias: PLAN_LINE

    02: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    : name: RECORD_SOURCE_ID alias: RECORD_SOURCE_ID

    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    : name: PARENT_RECORD_SOURCE_ID alias: PARENT_RECORD_SOURCE_ID

    04: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    : name: LEVEL alias: LEVEL

    05: sqltype: 500 SHORT Nullable scale: 0 subtype: 0 len: 2
    : name: OBJECT_TYPE alias: OBJECT_TYPE

    06: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 252 charset: 4 UTF8
    : name: PACKAGE_NAME alias: PACKAGE_NAME

    07: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 252 charset: 4 UTF8
    : name: OBJECT_NAME alias: OBJECT_NAME

    08: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 252 charset: 4 UTF8
    : name: ALIAS alias: ALIAS

    09: sqltype: 480 DOUBLE Nullable scale: 0 subtype: 0 len: 8
    : name: CARDINALITY alias: CARDINALITY

    10: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
    : name: RECORD_LENGTH alias: RECORD_LENGTH

    11: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
    : name: KEY_LENGTH alias: KEY_LENGTH

    12: sqltype: 520 BLOB scale: 0 subtype: 1 len: 8 charset: 4 UTF8
    : name: ACCESS_PATH alias: ACCESS_PATH
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
