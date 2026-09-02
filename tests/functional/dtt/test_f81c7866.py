#coding:utf-8

"""
ID:          n/a
ISSUE:       https://groups.google.com/g/firebird-devel/c/Deaz3vZerhI/m/ldmo2lCGAQAJ
TITLE:       DECLARED TEMP TABLE. Error "SQLSTATE = 22000 / no current record for fetch" may unexpectedly raise
DESCRIPTION:
NOTES:
    [02.09.2026] pzotov
    Fix: https://github.com/FirebirdSQL/firebird/commit/f81c7866c5df1cd54bc4618f09b0bb09dd42b5b2
    Confirmed bug on 6.0.0.2164-2d371e2.
    Checked on 6.0.0.2166-f81c786.
"""
import pytest
from firebird.qa import *

db = db_factory()
substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_sql = """
        set bail on;
        set list on;
        set autoterm on;
        execute block returns(cnt int) as
            declare temporary table ltt_test(txt varchar(10));
        begin
            insert into ltt_test(txt) values('foo');
            for
                select txt
                from ltt_test
                as cursor c
            do begin
                select 1 from ltt_test u
                where u.txt= c.txt
                order by 1
                rows 1
                into cnt;
                suspend;
            end
        end;
    """

    expected_stdout = f"""
        CNT 1
    """
    act.expected_stdout = expected_stdout

    act.isql(switches=['-q'], combine_output = True, input = test_sql)
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
