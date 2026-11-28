# coding:utf-8

"""
ID:          utilites.gbak.tablespace.ts_to_primary
TITLE:       Test the moving of TS contents to the primary database at the restore
DESCRIPTION: 
    Creates 3 tables and 3 indexes in three different user-defined tablespaces.
    Performs backup and restore:
    - 2 tablespaces are redirected to PRIMARY (one via -ts, one via -ts_map),
    - 1 tablespace remains as a separate tablespace.
    Verifies that after restore the objects from the first two tablespaces are placed
    into the primary database file, while the third tablespace and its contents remain unchanged.
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()
act = python_act('db')

expected_output = """
TABLESPACES
===========
TS3

TS1_TESTTABLE
=============
Table: PUBLIC.TS1_TESTTABLE
TS_ID                           INTEGER Nullable
TS_DESC                         VARCHAR(50) CHARACTER SET SYSTEM.NONE Nullable

TS2_TESTTABLE
=============
Table: PUBLIC.TS2_TESTTABLE
TS_ID                           INTEGER Nullable
TS_DESC                         VARCHAR(50) CHARACTER SET SYSTEM.NONE Nullable

TS3_TESTTABLE
=============
Table: PUBLIC.TS3_TESTTABLE
TABLESPACE: TS3
TS_ID                           INTEGER Nullable
TS_DESC                         VARCHAR(50) CHARACTER SET SYSTEM.NONE Nullable

TS_INDEXES
==========
PUBLIC.TS1_INDEX INDEX ON PUBLIC.TS1_TESTTABLE(TS_DESC)
PUBLIC.TS2_INDEX INDEX ON PUBLIC.TS2_TESTTABLE(TS_DESC)
PUBLIC.TS3_INDEX INDEX ON PUBLIC.TS3_TESTTABLE TABLESPACE TS3(TS_DESC)
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path):
    ts1_file = tmp_path / 'ts1_file.dat'
    ts2_file = tmp_path / 'ts2_file.dat'
    ts3_file = tmp_path / 'ts3_file.dat'

    restore_dsn = tmp_path / 'test_db_restore.fdb'
    backup_dsn = tmp_path / 'test_db_backup.fbk'

    script = f"""
    CREATE TABLESPACE TS1 FILE '{ts1_file}';
    CREATE TABLESPACE TS2 FILE '{ts2_file}';
    CREATE TABLESPACE TS3 FILE '{ts3_file}';

    CREATE TABLE TS1_TestTable (TS_ID int, TS_Desc varchar(50)) TABLESPACE TS1;
    CREATE TABLE TS2_TestTable (TS_Id int, TS_Desc varchar(50)) TABLESPACE TS2;
    CREATE TABLE TS3_TestTable (TS_Id int, TS_Desc varchar(50)) TABLESPACE TS3;

    CREATE INDEX TS1_Index ON TS1_TestTable(TS_Desc) TABLESPACE TS1;
    CREATE INDEX TS2_Index ON TS2_TestTable(TS_Desc) TABLESPACE TS2;
    CREATE INDEX TS3_Index ON TS3_TestTable(TS_Desc) TABLESPACE TS3;
    """
    act.isql(switches=['-q'], input=script)

    act.gbak(switches=['-B', act.db.dsn, backup_dsn])

    map_ts = tmp_path / 'map_ts.txt'
    mapping_ts = f"""
TS2 PRIMARY
TS3 'not_primary.dat'
"""
    map_ts.write_text(mapping_ts)

    act.gbak(switches=['-C', backup_dsn, restore_dsn, '-ts_map', map_ts, '-ts', 'TS1', 'PRIMARY'])

    test_script = """
    select '' as Tablespaces from rdb$database;
    SHOW TABLESPACES;

    select '' as TS1_TestTable from rdb$database;
    SHOW TABLE TS1_TestTable;
    
    select '' as TS2_TestTable from rdb$database;
    SHOW TABLE TS2_TestTable;
    
    select '' as TS3_TestTable from rdb$database;
    SHOW TABLE TS3_TestTable;

    select '' as TS_Indexes from rdb$database;
    SHOW INDEXES;
    """
    act.isql(switches=[restore_dsn, '-q'], input=test_script, connect_db=False)   

    act.expected_stdout = expected_output
    assert act.clean_stdout == act.clean_expected_stdout
