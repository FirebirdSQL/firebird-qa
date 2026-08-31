#coding:utf-8

"""
ID:          n/a
ISSUE:       n/a
TITLE:       DECLARED TEMPORARY TABLE. Index usage in DML that is running in autonomous transaction.
DESCRIPTION:
    Test verifies that DML running within autonomous Tx:
        1) does see same rows that did appear in the DTT before this autonomous Tx started;
        2) involves index that has been created in the DTT declaration (particulary, uniqueness is checked).
    Also, test checks that UNICODE_CI_AI collation works for DTT as usual for other kinds of tables, namely:
    if appropriate field has unique index then we can not insert two lines that differ on case or accent only.
NOTES:
    Original commit:
        https://github.com/FirebirdSQL/firebird/commit/f93b6ce7ba148e6185c40a3328ca56686626e2ae

    [31.08.2026] pzotov
    Checked on 20260829_024127-6.0.0.2164-2d371e2.
"""
import locale
import pytest
from firebird.qa import *

db = db_factory(charset = 'utf8')

substitutions = [('[ \t]+', ' '), (r'line: \d+, col: \d+', '')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    UTF8_CI_AI_CHECK_VAL = 'Procházky Starým Městem'

    test_script = f"""
        SET BAIL ON; -- [ 1 ]
        set list on;
        set autoterm on;
        commit;
        create domain dm_txt_ci_ai varchar(100) character set utf8 collate unicode_ci_ai;

        create or alter procedure sp_test_1 returns(exc_gdscode int, exc_message varchar(8190)) as
            declare temporary table tbase1(id int)
            UNIQUE index tbase1_id_unq(id)
            ;
        begin
            insert into tbase1(id) values(1);
            begin
                in autonomous transaction do
                begin
                    insert into tbase1(id) select id from tbase1;
                end
            when any do
                begin
                    exc_gdscode = gdscode;
                    exc_message = ascii_char(10) || rdb$error(message);
                end
            end
            suspend;
        end;

        create or alter procedure sp_test_2 returns(exc_gdscode int, exc_message varchar(8190)) as
            declare temporary table tbase2(txt dm_txt_ci_ai)
            UNIQUE index tbase2_id_unq(txt)
            ;
        begin
            insert into tbase2(txt) values('{UTF8_CI_AI_CHECK_VAL}');
            begin
                in autonomous transaction do
                begin
                    insert into tbase2(txt) select upper(txt) from tbase2;
                end
            when any do
                begin
                    exc_gdscode = gdscode;
                    exc_message = ascii_char(10) || rdb$error(message);
                end
            end
            suspend;
        end;

        select p.* from sp_test_1 p;
        select p.* from sp_test_2 p;
    """

    act.expected_stdout = f"""
        EXC_GDSCODE 335544349
        EXC_MESSAGE
        attempt to store duplicate value (visible to active transactions) in unique index "TBASE1_ID_UNQ"
        Problematic key value is ("ID" = 1)
        At procedure "PUBLIC"."SP_TEST_1"

        EXC_GDSCODE 335544349
        EXC_MESSAGE
        attempt to store duplicate value (visible to active transactions) in unique index "TBASE2_ID_UNQ"
        Problematic key value is ("TXT" = '{UTF8_CI_AI_CHECK_VAL.upper()}')
        At procedure "PUBLIC"."SP_TEST_2"
    """
    act.isql(switches=['-q'], charset = 'utf8', input = test_script, combine_output = True, io_enc = 'utf-8')
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

