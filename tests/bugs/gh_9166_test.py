#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9166
TITLE:       Failed COMMIT of Tx with 'ALTER TABLE' leaves orphan RDB$FORMATS records causing subsequent "bugcheck 179 Record N is wrong length" for new tables
DESCRIPTION:
    Test uses simplified scenario from ticket and checks output of ISQL, then running `gfix -v -full` and compare firebird.log with its initial state.
NOTES:
    [11.10.2026] pzotov
    Before fix, versions 3x ... 5x failed with bugcheck "decompression overran buffer (179), file: sqz.cpp line: ..."
    Validation failed with "Error: Record 1 is wrong length in table EXISTING_TABLE (...)"

    Test uses same pattern as test for #9160: .sql script, validation and check of firebird.log content.
    Fixing commits:
        5x: https://github.com/FirebirdSQL/firebird/commit/877b981f0015452249d736284b0e34eddf58ac38
        4x: https://github.com/FirebirdSQL/firebird/commit/06b44f2deda9245868f2a18436850a7c6401e72b
        3x: https://github.com/FirebirdSQL/firebird/commit/a125e4e9fa09e271d66165bca1a181e307ff7154

    ::: ACHTUNG :::
    It is doubtful that FB 6.x behaves as expected! Columns 'extra_1' and 'extra_2' must not appear in the table after failed commit
    of Tx that contained both 'alter table add ...' and 'create UNIQUE index' (which failed because of duplicates).
    Because of that, execution on 6.x currently is SKIPPED. Checked on 6.0.0.2208-6515630.

    Confirmed bug on 5.0.5.1891-22e4dec; 4.0.8.3322-0c6f6b0; 3.0.15.33886-8a45b62.
    Checked on 5.0.5.1893-e5e4d33; 4.0.8.3328-dc6ab10; 3.0.15.33889-4ebf3b1.
"""
import re
import locale
from difflib import unified_diff
import pytest
from firebird.qa import *

db = db_factory()
substitutions = [('[ \t]+', ' '), ('DBKEY_BLOB_ID.*', 'DBKEY_BLOB_ID')] 
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=3.0.15')
def test_1(act: Action, capsys):

    if act.is_version('<6'):
        pass
    else:
        pytest.skip('Output seems not expected. SEE NOTES.')

    test_script = f"""
        set bail on;
        set list on;

        -- Step 1: an existing table with data, filler tables, then ALTER TABLE in a transaction
        -- whose COMMIT fails during deferred work. The new format 2 of the existing table remains.

        create table dup_data (code integer);
        create table existing_table (id integer);
        commit;
        insert into dup_data values (1);
        insert into dup_data values (1);
        insert into existing_table values (1);
        commit;

        -- Filler tables occupy RDB$FORMATS slots located before the format created below
        create table filler_1 (id integer, txt varchar(100));
        create table filler_2 (id integer, txt varchar(100));
        create table filler_3 (id integer, txt varchar(100));
        create table filler_4 (id integer, txt varchar(100));
        create table filler_5 (id integer, txt varchar(100));
        commit;

        set bail OFF;

        set autoddl off;
        alter table existing_table add extra_1 bigint, add extra_2 bigint;
        create unique index dup_data_code_unq on dup_data (code);
        -- Expected: COMMIT fails with "attempt to store duplicate value"
        commit;
        rollback;
        set autoddl on;

        set bail ON;

        -- Expected: only format 1. Actual: format 2 of the rolled-back ALTER remains
        select f.rdb$format as point_a_rdb_fmt, f.rdb$db_key as dbkey_blob_id
        from rdb$formats f
        join rdb$relations r on r.rdb$relation_id = f.rdb$relation_id
        where r.rdb$relation_name = 'EXISTING_TABLE'
        order by f.rdb$db_key;

        drop table filler_1;
        drop table filler_2;
        drop table filler_3;
        drop table filler_4;
        drop table filler_5;
        commit;

        --------------------------------------------

        -- Step 2: a successful ALTER TABLE creates format 2 again, stored in a freed slot.
        -- Rows written in this attachment use the in-memory format and read back correctly.

        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';
        select count(*) as point_b_fmt_count from rdb$formats;
        commit;

        alter table existing_table add txt varchar(255);
        commit;
        insert into existing_table (id, txt) values (2, 'test');
        commit;
        select * from existing_table;

        select f.rdb$format as point_b_rdb_fmt, f.rdb$db_key as dbkey_blob_id
        from rdb$formats f
        join rdb$relations r on r.rdb$relation_id = f.rdb$relation_id
        where r.rdb$relation_name = 'EXISTING_TABLE'
        order by f.rdb$db_key;
        commit;

        --------------------------------------------

        -- Step 3: new attachment, formats loaded from RDB$FORMATS.
        -- Expected: rows 1 and 2. Actual: row 1, then consistency check (decompression overran buffer (179))

        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';
        select count(*) point_c_fmt_count from rdb$formats;
        commit;

        select * from existing_table;
    """

    log_before = act.get_firebird_log()

    act.isql(switches = ['-q'], input = test_script, combine_output = True, io_enc = 'utf-8' )
    actual_out = act.clean_stdout
    act.reset()

    #---------------------------------------
    act.gfix(switches=['-v', '-full', act.db.db_path], combine_output = True, io_enc = locale.getpreferredencoding())
    if act.clean_stdout:
        actual_out += '\n' + 'Unexpected output in gfix:\n' + act.clean_stdout
    act.reset()
    #---------------------------------------

    log_after = act.get_firebird_log()

    allowed_patterns = [ r'consistency\s+check', 'Error:', r'wrong\s+length' ]
    allowed_patterns = [ re.compile(x, re.IGNORECASE) for x in allowed_patterns ]
    print_title_msg = 1
    for line in unified_diff(log_before, log_after):
        if (msg := line.strip()):
            if msg.startswith('+') and act.match_any(msg, allowed_patterns):
                if print_title_msg:
                    actual_out += '\n' + 'Unexpected messages in firebird.log:'
                    print_title_msg = 0
                actual_out += '\n' + msg

    print(actual_out)

    expected_out_5x = """
        Statement failed, SQLSTATE = 23000
        attempt to store duplicate value (visible to active transactions) in unique index "DUP_DATA_CODE_UNQ"
        -Problematic key value is ("CODE" = 1)

        POINT_A_RDB_FMT                 1
        DBKEY_BLOB_ID                   08000000E2010000
        
        POINT_B_FMT_COUNT               2
        
        ID                              1
        TXT                             <null>
        
        ID                              2
        TXT                             test
        
        POINT_B_RDB_FMT                 1
        DBKEY_BLOB_ID                   08000000E2010000
        
        POINT_B_RDB_FMT                 2
        DBKEY_BLOB_ID                   08000000E3010000
        
        POINT_C_FMT_COUNT               3
        
        ID                              1
        TXT                             <null>
        
        ID                              2
        TXT                             test
    """

    expected_out_6x = """
        Statement failed, SQLSTATE = 23000
        unsuccessful metadata update
        -CREATE INDEX "PUBLIC"."DUP_DATA_CODE_UNQ" failed
        -attempt to store duplicate value (visible to active transactions) in unique index "PUBLIC"."DUP_DATA_CODE_UNQ"
        -Problematic key value is ("CODE" = 1)

        POINT_A_RDB_FMT                 1
        DBKEY_BLOB_ID                   08000000E2010000

        POINT_A_RDB_FMT                 2
        DBKEY_BLOB_ID                   08000000E8010000
        
        POINT_B_FMT_COUNT               3
        
        ID                              1
        EXTRA_1                         <null>
        EXTRA_2                         <null>
        TXT                             <null>
        
        ID                              2
        EXTRA_1                         <null>
        EXTRA_2                         <null>
        TXT                             test
        
        POINT_B_RDB_FMT                 1
        DBKEY_BLOB_ID                   08000000E2010000
        
        POINT_B_RDB_FMT                 3
        DBKEY_BLOB_ID                   08000000E3010000
        
        POINT_B_RDB_FMT                 2
        DBKEY_BLOB_ID                   08000000E8010000

        POINT_C_FMT_COUNT               4
        
        ID                              1
        EXTRA_1                         <null>
        EXTRA_2                         <null>
        TXT                             <null>
        
        ID                              2
        EXTRA_1                         <null>
        EXTRA_2                         <null>
        TXT                             test
    """

    act.expected_stdout = expected_out_5x if act.is_version('<6') else expected_out_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
