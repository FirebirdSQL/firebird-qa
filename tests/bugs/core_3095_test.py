#coding:utf-8

"""
ID:          issue-3474
ISSUE:       3474
TITLE:       Client receive event's with count equal to 1 despite of how many times EVENT was POSTed in same transaction
DESCRIPTION:
  We create stored procedure as it was specified in the ticket, and call it with input arg = 3.
  This mean that we have to receive THREE events after code which calls this SP will issue COMMIT.
JIRA:        CORE-3095
"""

import pytest
from firebird.qa import *

init_script = """
    set term ^;
    create or alter procedure sp_test (a_evt_count int) as
    begin
        while (a_evt_count > 0) do
        begin
            post_event('loop');
            a_evt_count = a_evt_count - 1;
        end
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db')

expected_stdout = """
   {'loop': 3}
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    act.expected_stdout = expected_stdout
    with act.db.connect() as con:
        c = con.cursor()
        with con.event_collector(['loop']) as events:
            c.execute('execute procedure sp_test(3)')
            con.commit()
            print(events.wait(10))
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
