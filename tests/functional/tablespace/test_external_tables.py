# coding:utf-8

"""
ID:          functional.tablespace.external_tables
TITLE:       External tables cannot be assigned to tablespaces
DESCRIPTION:
  Verifies that external tables cannot be associated with tablespaces.
  Attempts to ALTER or CREATE external tables with tablespace should fail.
"""

import pytest
from firebird.qa import *
from pathlib import Path

db = db_factory()
act = python_act('db', substitutions=[('===*', '============')])

expected_stdout = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE "PUBLIC"."EXT_EMPLOYEES" failed
    -Cannot set tablespace for external table "PUBLIC"."EXT_EMPLOYEES"

    RDB$RELATION_NAME                                               RDB$TABLESPACE_NAME
    ============ ============
    EXT_EMPLOYEES                                                   <null>

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE TABLE "PUBLIC"."EXT_EMPLOYEES_2" failed
    -Cannot set tablespace for external table "PUBLIC"."EXT_EMPLOYEES_2"

    There is no table EXT_EMPLOYEES_2 in this database
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    employees_csv = tmp_path / 'employees.csv'
    ts_file = tmp_path / 'ts1.dat'

    init_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts_file.resolve()}';
    CREATE TABLE ext_employees EXTERNAL FILE '{employees_csv.resolve()}' (
        id INTEGER,
        name VARCHAR(100),
        posit VARCHAR(100),
        salary DECIMAL(10,2)
    );
    """

    act.isql(switches=['-q'], input=init_script, combine_output=True)
    act.reset()

    test_script = f"""
    ALTER TABLE ext_employees SET TABLESPACE ts1;
    commit;

    SELECT r.rdb$relation_name, r.rdb$tablespace_name
    FROM rdb$relations r
    WHERE r.rdb$relation_name = 'EXT_EMPLOYEES';

    CREATE TABLE ext_employees_2 EXTERNAL FILE '{employees_csv.resolve()}' (
        id INTEGER,
        name VARCHAR(100),
        posit VARCHAR(100),
        salary DECIMAL(10,2)
    ) TABLESPACE ts1;
    commit;

    show table EXT_EMPLOYEES_2;
    """

    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=test_script, combine_output=True)

    assert act.clean_stdout == act.clean_expected_stdout
