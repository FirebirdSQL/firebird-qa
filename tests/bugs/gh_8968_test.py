#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8968
TITLE:       Incorrect check of the limit on the number of local temporary tables
DESCRIPTION:
NOTES:
    [01.04.2026] pzotov
    Confirmed bug on 6.0.0.1867-3da484c.
    Checked on 6.0.0.1870-7464f45.
"""
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set autoterm on;
    set list on;
    execute block as
        declare idx int;
    begin
        in autonomous transaction do
        begin
            for idx = 1 to 10000 do   
                execute statement 'recreate local temporary table a_'||:idx||' (id int) on commit preserve rows';
        end
    end;
    select count(*) from mon$local_temporary_tables;
"""

substitutions = [('[ \t]+', ' '), ('(-)?At block .*', ''), ('RECREATE TABLE .* failed', 'RECREATE TABLE failed')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    Statement failed, SQLSTATE = 54000
    unsuccessful metadata update
    -RECREATE TABLE failed
    -Implementation limit exceeded
    -Too many local temporary tables exist already
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
