#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8881
TITLE:       Large amount of unnecessary privileges in RDB$USER_PRIVILEGES for SYSDBA
DESCRIPTION:
NOTES:
    [18.03.2026] pzotov
    Thanks to dimitr for suggestion related to test implementation details.
    Confirmed problem on 6.0.0.1816-0c91d1a; 5.0.4.1780-8824b2e
    Checked on: 6.0.0.1819-61354ae; 5.0.4.1783-efed600.
"""
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    set term ^;
    execute block as
        declare n int = 5;
        declare i int;
        declare s blob sub_type text;
    begin
        s = 'create table test(';
        i = n;
        while (i>0) do
        begin
            s = blob_append(s, 'f_' || i || ' int ',  iif(i>1, ',', ''));
            i = i - 1;
        end
        s = blob_append(s, ')');
        execute statement(s)
        with autonomous transaction
        ;
        -----------------------------
        s = 'alter table test ';
        i = n - 1;
        while (i>0) do
        begin
            s = blob_append(s, 'drop f_' || i,  iif(i>1, ',', ''));
            i = i - 1;
        end
        s = blob_append(s, ';');
        execute statement(s)
        with autonomous transaction
        ;
    end
    ^
    set term ;^
    commit;

    set count on;
    select p.*
    from rdb$user_privileges p
    where
    rdb$privilege = 'G'
    and p.rdb$relation_name like 'RDB$%'
    and trim(substring(p.rdb$relation_name from 5)) similar to '[[:DIGIT:]]+'
    ;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.version('>=5.0.4')
def test_1(act: Action):
    expected_stdout = """
        Records affected: 0
    """
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
