#coding:utf-8

"""
ID:          n/a
ISSUE:       n/a
TITLE:       DECLARED TEMPORARY TABLE. An autonomous transaction must see the same rows.
DESCRIPTION:
NOTES:
    [28.07.2026] pzotov
    An issue was found during implementation:
    https://groups.google.com/g/firebird-devel/c/jiZK-5cfVYU/m/j7B5saitBwAJ
    Fix: https://github.com/FirebirdSQL/firebird/commit/2b4ec4435c1f14f59e2f7c970b832a6dd008147e
    Checked 6.0.0.2097-0592438 -- all fine.
"""
import locale
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    test_script = """
        SET BAIL ON; -- [ 1 ]
        set list on;
        set autoterm on;
        commit;

        -- This caused FB hang:
        create or alter procedure sp_test_1 returns(id int) as
            declare temporary table tbase(id int);
        begin
            insert into tbase(id) values(-1);
            in autonomous transaction do
            begin
                insert into tbase(id) select -id from tbase;
            end
            for
                select id from tbase into id
            do begin
                suspend;
            end
        end;

        -- This caused SQLSTATE = 22003 / arithmetic exception, numeric overflow, ... / -numeric value is out of range        
        create or alter procedure sp_test_2 returns(id int) as
            declare temporary table tbase(id int);
        begin
            insert into tbase(id) values(-1);
            in autonomous transaction do
            begin
                insert into tbase(id) select -2 * id from tbase;
            end
            for
                select id from tbase into id
            do begin
                suspend;
            end
        end;

        select p.id as sp_1_result from sp_test_1 p;
        select p.id as sp_2_result from sp_test_2 p;
    """

    act.expected_stdout = """
        SP_1_RESULT -1
        SP_1_RESULT 1
        SP_2_RESULT -1
        SP_2_RESULT 2
    """
    act.isql(switches=['-q'], input = test_script, combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
