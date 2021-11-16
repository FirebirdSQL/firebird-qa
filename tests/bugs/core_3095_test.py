#coding:utf-8
#
# id:           bugs.core_3095
# title:        Client receive event's with count equal to 1 despite of how many times EVENT was POSTed in same transaction
# decription:
#                   We create stored procedure as it was specified in the ticket, and call it with input arg = 3.
#                   This mean that we have to receive THREE events after code which calls this SP will issue COMMIT.
#
#                   Confirmed on 2.5.0.26074 - only one event was delivered instead of three.
#                   Works OK since 2.5.1.26351.
#
#                   PS. Event handling code in this text was adapted from fdb manual:
#                   http://pythonhosted.org/fdb/usage-guide.html#database-events
#
# tracker_id:   CORE-3095
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import threading
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  # Utility function
#  def send_events(command_list):
#     cur = db_conn.cursor()
#     for cmd in command_list:
#        cur.execute(cmd)
#     db_conn.commit()
#
#  timed_event = threading.Timer(3.0, send_events, args=[["execute procedure sp_test(3)",]])
#
#  # Connection.event_conduit() takes a sequence of string event names as parameter, and returns
#  # EventConduit instance.
#  events = db_conn.event_conduit(['loop'])
#
#  # To start listening for events it's necessary (starting from FDB version 1.4.2)
#  # to call EventConduit.begin() method or use EventConduit's context manager interface
#  # Immediately when begin() method is called, EventConduit starts to accumulate notifications
#  # of any events that occur within the conduit's internal queue until the conduit is closed
#  # (via the close() method)
#
#  events.begin()
#
#  timed_event.start()
#
#  # Notifications about events are aquired through call to wait() method, that blocks the calling
#  # thread until at least one of the events occurs, or the specified timeout (if any) expires,
#  # and returns None if the wait timed out, or a dictionary that maps event_name -> event_occurrence_count.
#
#  e = events.wait(10)
#
#  events.close()
#
#  print(e)
#  db_conn.close()
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
   {'loop': 3}
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, capsys):
    act_1.expected_stdout = expected_stdout_1
    with act_1.db.connect() as con:
        c = con.cursor()
        with con.event_collector(['loop']) as events:
            c.execute('execute procedure sp_test(3)')
            con.commit()
            print(events.wait(10))
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
