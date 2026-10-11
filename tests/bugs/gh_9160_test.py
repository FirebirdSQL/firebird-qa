#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9160
TITLE:       Failed COMMIT of a DDL transaction leaves orphan RDB$FORMATS records causing subsequent "bugcheck 179 Record N is wrong length" for new tables
DESCRIPTION:
    Test uses simplified scenario from ticket and checks output of ISQL, then running `gfix -v -full` and compare firebird.log with its initial state.
NOTES:
    Confirmed bug on 5.0.5.1888-9b169bc; 4.0.8.3322-a2c43e7; 3.0.15.33886-71590ee.
    Checked on 6.0.0.2208-6515630; 5.0.5.1891-22e4dec; 4.0.8.3322-0c6f6b0; 3.0.15.33886-8a45b62
"""
import re
import locale
from difflib import unified_diff
import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db')

@pytest.mark.version('>=3.0.15')
def test_1(act: Action, capsys):

    test_script = f"""
        set bail on;
        set list on;

        -- Step 1: create filler tables, fail a DDL transaction at COMMIT, drop the fillers.
        -- The failed transaction leaves RDB$FORMATS records of relations that were rolled back.

        create table dup_data (code integer);
        commit;
        insert into dup_data values (1);
        insert into dup_data values (1);
        commit;

        -- Filler tables occupy RDB$FORMATS slots located before the formats created below
        create table filler_1 (id integer, txt varchar(100));
        create table filler_2 (id integer, txt varchar(100));
        create table filler_3 (id integer, txt varchar(100));
        create table filler_4 (id integer, txt varchar(100));
        create table filler_5 (id integer, txt varchar(100));
        commit;

        set term ^;
        execute block as
        begin
            rdb$set_context( 'USER_SESSION', 'REL_ID_COUNTER_INI', (select rdb$relation_id from rdb$database) );
        end ^
        set term ;^

        -- One transaction: three new tables + a unique index that can only fail at COMMIT
        set bail OFF;
        set autoddl off;
        create table orphan_1 (id bigint, parent_id bigint, num smallint);
        create table orphan_2 (id bigint, parent_id bigint, num smallint);
        create table orphan_3 (id bigint, parent_id bigint, num smallint);
        create unique index dup_data_code_unq on dup_data (code);
        -- Expected: COMMIT fails with "attempt to store duplicate value"
        commit;
        
        ROLLBACK;

        set autoddl on;
        set bail ON;

        -- The relation ID counter must be rolled back together with RDB$RELATIONS.
        set term ^;
        execute block returns( rel_id_diff_msg varchar(255) ) as
            declare rel_id_counter_ini int;
            declare rel_id_counter_cur int;
        begin
            rel_id_counter_ini = rdb$get_context( 'USER_SESSION', 'REL_ID_COUNTER_INI');
            select rdb$relation_id from rdb$database into rel_id_counter_cur;
            if (rel_id_counter_ini = rel_id_counter_cur) then
                rel_id_diff_msg = 'EXPECTED: NOT CHANGED.';
            else
                rel_id_diff_msg = 'UNEXPECTED: rel_id_counter_ini='
                    || coalesce(rel_id_counter_ini, '[null]')
                    || ', rel_id_counter_cur='
                    || coalesce(rel_id_counter_cur, '[null]')
                ;
        
            suspend;

        end ^
        set term ;^

        -- Expected: no rows. Actual: formats of the rolled-back relations remain
        select
            f.rdb$relation_id as unexpected_rel_id
            ,f.rdb$format as unexpected_format
            --,f.rdb$db_key as physical_position
        from rdb$formats f
        where not exists (select 1 from rdb$relations r
                          where r.rdb$relation_id = f.rdb$relation_id)
        order by f.rdb$relation_id
        ;

        -- Dropping the fillers frees their RDB$FORMATS slots (after garbage collection / sweep)
        drop table filler_1;
        drop table filler_2;
        drop table filler_3;
        drop table filler_4;
        drop table filler_5;
        commit;

        ----------------------------------------- 2 ---------------------------------------------
        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';
        --select count(*) from rdb$formats;

        -- Step 2: new tables reuse the relation IDs of the orphan formats.
        -- Their formats are stored in the slots freed by the fillers, i.e. before the orphan records.

        create table victim_a (txt varchar(255));
        commit;
        insert into victim_a values ('test');
        commit;
        -- Works: this attachment uses the format built in memory by CREATE TABLE
        select a.txt as chk_txt_1 from victim_a a;
        commit;

        ----------------------------------------- 3 ---------------------------------------------
        connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';

        -- Step 3: new attachment, the format of VICTIM_A is loaded from RDB$FORMATS.
        -- Expected: one row 'test'.
        -- Actual: internal Firebird consistency check (decompression overran buffer (179))
        set bail off;
        select a.txt as chk_txt_2 from victim_a a;
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
        REL_ID_DIFF_MSG                 EXPECTED: NOT CHANGED.
        CHK_TXT_1                       test
        CHK_TXT_2                       test
    """

    expected_out_6x = """
        Statement failed, SQLSTATE = 23000
        unsuccessful metadata update
        -CREATE INDEX "PUBLIC"."DUP_DATA_CODE_UNQ" failed
        -attempt to store duplicate value (visible to active transactions) in unique index "PUBLIC"."DUP_DATA_CODE_UNQ"
        -Problematic key value is ("CODE" = 1)
        REL_ID_DIFF_MSG                 EXPECTED: NOT CHANGED.
        CHK_TXT_1                       test
        CHK_TXT_2                       test
    """

    act.expected_stdout = expected_out_5x if act.is_version('<6') else expected_out_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
