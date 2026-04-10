#coding:utf-8
"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8957
TITLE:       AllowUpdateOverwrite config setting: how UPDATE should handle the case when a record was updated by trigger
DESCRIPTION:
    Test uses pre-created databases.conf which has alias (see variable REQUIRED_ALIAS) with AllowUpdateOverwrite = false.
    This value must cause error raising when UPDATE statement will overwrite changes made by the trigger.
    Database file for that alias must NOT exist in the QA_root/files/qa/ subdirectory: it will be created here.
NOTES:
    [11.04.2026] pzotov
    Checked on 6.0.0.1887, 5.0.7.1808
"""
import locale
import re
import os
from pathlib import Path

import pytest
from firebird.qa import *

REQUIRED_ALIAS = 'tmp_gh_8957_alias'

db = db_factory(filename = '#' + REQUIRED_ALIAS)
substitutions = [('[ \t]+', ' '), ]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=5.0.4')
def test_1(act: Action, capsys):
    
    # Scan line-by-line through databases.conf, find line starting with REQUIRED_ALIAS and extract name of file that
    # must be created in the $(dir_sampleDb)/qa/ folder.
    # NOTE: we have to SKIP lines which are commented out, i.e. if they starts with '#':
    p_required_alias_ptn =  re.compile( '^(?!#)((^|\\s+)' + REQUIRED_ALIAS + ')\\s*=\\s*\\$\\(dir_sampleDb\\)/qa/', re.IGNORECASE )
    fname_in_dbconf = None

    with open(act.home_dir/'databases.conf', 'r') as f:
        for line in f:
            if p_required_alias_ptn.search(line):
                # If databases.conf contains line like this:
                #     tmp_8957_alias = $(dir_sampleDb)/qa/tmp_qa_8957.fdb 
                # - then we extract filename: 'tmp_qa_8957.fdb' (see below):
                fname_in_dbconf = Path(line.split('=')[1].strip()).name
                break

    # if 'fname_in_dbconf' remains undefined here then propably REQUIRED_ALIAS not equals to specified in the databases.conf!
    #
    assert fname_in_dbconf

    test_sql = f"""
        set list on;
        set count on;
        select rdb$config_name, rdb$config_value from rdb$config where rdb$config_name = 'AllowUpdateOverwrite';
        set count off;
        commit;

        create table test_a (
            id int,
            amt numeric(9,2),
            sta int
        );
        create table test_b (
            id int,
            amt numeric(9,2),
            sta int
        );
        commit;

        set term ^;
        execute block as
            declare i int = 0;
            declare n int = 3;
        begin
            while (i < n) do
            begin
                insert into test_a(id, amt, sta) values(:i+1, (1+:i) * 100, 1);
                insert into test_b(id, amt, sta) values(:i+1, (1+:i) * 100, 1);
                i = i + 1;
            end
        end
        ^
        create or alter trigger trg_test_b_biu for test_b active BEFORE insert or update as
        begin
              if (new.sta is distinct from old.sta) then
                  begin
                      rdb$set_context('USER_TRANSACTION', 'TRG_TEST_B_BIU FIRED: OLD.STA, NEW.STA ==> ', coalesce(old.sta, '[null]') || ', ' || coalesce(new.sta, '[null]') );
                      execute statement ('update test_b set amt = amt + 67 where id = ?') (new.id + 1);
                  end
              else
                  rdb$set_context('USER_TRANSACTION', 'TRG_TEST_B_BIU FIRED: OLD.STA is NOT distinct from NEW.STA ==> ', coalesce(old.sta, '[null]') || ', ' || coalesce(new.sta, '[null]') );
        end
        ^
        create or alter trigger trg_test_a_aiu for test_a active AFTER insert or update as
        begin
              if (new.sta is distinct from old.sta) then
                  begin
                      rdb$set_context('USER_TRANSACTION', 'TRG_TEST_A_AIU FIRED: OLD.STA, NEW.STA ==> ', coalesce(old.sta, '[null]') || ', ' || coalesce(new.sta, '[null]') );
                      execute statement ('update test_a set amt = amt - 33 where id = ?') (new.id - 1);
                  end
              else
                  rdb$set_context('USER_TRANSACTION', 'TRG_TEST_A_AIU: OLD.STA is NOT distinct from NEW.STA ==> ', coalesce(old.sta, '[null]') || ', ' || coalesce(new.sta, '[null]') );
        end
        ^
        set term ;^
        commit;

        set list off;
        set heading off;
        select 'test_b point #0' msg from rdb$database;
        select t.* from test_b t order by id;

        select 'test_a point #0' msg from rdb$database;
        select t.* from test_a t order by id;
        commit;

        --##############################################
        set bail OFF;
        -- must raise SQLSTATE = 27000 / UPDATE will overwrite changes made by the trigger ...
        update test_b set sta = 2;

        -- must raise SQLSTATE = 27000 / UPDATE will overwrite changes made by the trigger ...
        update test_a set sta = 2 order by id desc;
        set bail ON;
        --##############################################

        -- Content must NOT changed (comparing to initial):
        select 'test_b point #1' msg from rdb$database;
        select t.* from test_b t order by id;

        -- Content must NOT changed (comparing to initial):
        select 'test_a point #1' msg from rdb$database;
        select t.* from test_a t order by id;
        rollback;
    """

    act.isql(switches=['-q'], input = test_sql, combine_output = True, io_enc = locale.getpreferredencoding())
    print(act.stdout)

    act.expected_stdout = """
        RDB$CONFIG_NAME AllowUpdateOverwrite
        RDB$CONFIG_VALUE false
        Records affected: 1
        
        test_b point #0
        1 100.00 1
        2 200.00 1
        3 300.00 1
        
        test_a point #0
        1 100.00 1
        2 200.00 1
        3 300.00 1
        
        Statement failed, SQLSTATE = 27000
        UPDATE will overwrite changes made by the trigger or by the another UPDATE in the same cursor
        
        Statement failed, SQLSTATE = 27000
        UPDATE will overwrite changes made by the trigger or by the another UPDATE in the same cursor

        test_b point #1
        1 100.00 1
        2 200.00 1
        3 300.00 1
        
        test_a point #1
        1 100.00 1
        2 200.00 1
        3 300.00 1
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
