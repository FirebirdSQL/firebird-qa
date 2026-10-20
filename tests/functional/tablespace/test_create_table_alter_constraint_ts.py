# coding:utf-8

"""
ID:          functional.tablespace.create_table_alter_constraint_ts
TITLE:       
DESCRIPTION:
FBTEST:      functional.tablespace.create_table_alter_constraint_ts
"""

import pytest
from pathlib import Path
from firebird.qa import *


db = db_factory()
act = isql_act('db')

expected_stdout = """
ID_PRIM                         123
ID_UNIQ                         777
VARCHAR_REF                     summer

ID_PRIM                         35
ID_UNIQ                         683
VARCHAR_REF                     winter

PRIMARY_TS                      TS1
UNIQUE_TS                       TS2
REFERENCES_TS                   PRIMARY

Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "TS_PRIM" on table "PUBLIC"."TEST_TABLE"
-Problematic key value is ("ID_PRIM" = 123)

Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "TS_UNIQ" on table "PUBLIC"."TEST_TABLE"
-Problematic key value is ("ID_UNIQ" = 683)

Statement failed, SQLSTATE = 23000
violation of FOREIGN KEY constraint "TS_REF" on table "PUBLIC"."TEST_TABLE"
-Foreign key reference target does not exist
-Problematic key value is ("VARCHAR_REF" = 'season')

PRIMARY_TS                      TS2
UNIQUE_TS                       PRIMARY
REFERENCES_TS                   TS1
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path):
    ts1_file = tmpdir / 'tablespace1.dat'
    ts2_file = tmpdir / 'tablespace2.dat'

    test_script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    CREATE TABLESPACE TS2 FILE '{ts2_file}';
    commit;

    CREATE TABLE REF_TABLE(ID INT, VARCHAR_REF VARCHAR(100) UNIQUE);
    INSERT INTO REF_TABLE VALUES (1, 'winter');
    INSERT INTO REF_TABLE VALUES (2, 'spring');
    INSERT INTO REF_TABLE VALUES (3, 'summer');
    INSERT INTO REF_TABLE VALUES (4, 'autumn');
    commit;

    CREATE TABLE TEST_TABLE(ID_PRIM     INT NOT NULL    CONSTRAINT          TS_PRIM     PRIMARY KEY                         IN TABLESPACE TS1,
                            ID_UNIQ     INT             CONSTRAINT          TS_UNIQ     UNIQUE                              TABLESPACE TS2,
                            VARCHAR_REF VARCHAR(100)    CONSTRAINT          TS_REF      REFERENCES   REF_TABLE(VARCHAR_REF) TABLESPACE PRIMARY);
    commit;

    INSERT INTO TEST_TABLE VALUES (123, 777, 'summer');
    INSERT INTO TEST_TABLE VALUES (35, 683, 'winter');
    commit;

    set list on;
    select * from TEST_TABLE;

    --CHECK CONSTRAINTS TABLESPACES--
    select RDB$TABLESPACE_NAME as PRIMARY_TS from RDB$INDICES where RDB$INDEX_NAME='TS_PRIM';
    select RDB$TABLESPACE_NAME as UNIQUE_TS from RDB$INDICES where RDB$INDEX_NAME='TS_UNIQ';
    select RDB$TABLESPACE_NAME as REFERENCES_TS from RDB$INDICES where RDB$INDEX_NAME='TS_REF';

    --CHANGE CONTRAINTS TABLESPACES--
    ALTER INDEX TS_PRIM SET TABLESPACE TS2;
    ALTER INDEX TS_UNIQ SET TABLESPACE PRIMARY;
    ALTER INDEX TS_REF SET TABLESPACE TS1;
    commit;

    --CHECK PRIMARY CONSTRAINT--
    INSERT INTO TEST_TABLE VALUES (123, 12365, 'autumn');
    --CHECK UNIQUE CONSTRAINT--
    INSERT INTO TEST_TABLE VALUES (555, 683, 'spring');
    --CHECK FOREIGN CONSTRAINT--
    INSERT INTO TEST_TABLE VALUES (654, 1212, 'season');

    --CHECK CONSTRAINTS TABLESPACES--
    select RDB$TABLESPACE_NAME as PRIMARY_TS from RDB$INDICES where RDB$INDEX_NAME='TS_PRIM';
    select RDB$TABLESPACE_NAME as UNIQUE_TS from RDB$INDICES where RDB$INDEX_NAME='TS_UNIQ';
    select RDB$TABLESPACE_NAME as REFERENCES_TS from RDB$INDICES where RDB$INDEX_NAME='TS_REF';
    """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=test_script, combine_output=True)

    assert act.clean_stdout == act.clean_expected_stdout
