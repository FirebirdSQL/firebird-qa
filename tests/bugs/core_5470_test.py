#coding:utf-8

"""
ID:          issue-5740-A
ISSUE:       5740-A
TITLE:       Trace INCLUDE_FILTER with [[:WHITESPACE:]]+ does not work when statement contains newline is issued
DESCRIPTION:
  We create a list of several DDLs which all contain NEWLINE character(s) between keyword and name of DB object.
  Then we launch trace session and execute all these DDLs.
  Finally we check whether trace log contains every DDL or not.
  Expected result: text of every DDL should be FOUND in the trace log.
JIRA:        CORE-5470
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

ddl_lst = ["""recreate

            table



            t_test(x int)
        """,
           """comment on
    table


    t_test is
            'foo
            bar'
    """,
"""

            create
    or

    alter
                    view

                    v_rio

                    as
                    select *
                    from

                    rdb$database
    """]

trace = ['time_threshold = 0',
         'log_initfini = false',
         'log_errors = true',
         'log_statement_finish = true',
         'include_filter = "%(recreate|create|alter|drop|comment on)[[:WHITESPACE:]]+(domain|generator|sequence|exception|procedure|function|table|index|view|trigger|role|filter|external function)%"',
         ]

@pytest.mark.version('>=3')
def test_1(act: Action):
    with act.trace(db_events=trace), act.db.connect() as con:
        for cmd in ddl_lst:
            con.execute_immediate(cmd)
        con.commit()
    # Check
    act.trace_to_stdout()
    for cmd in ddl_lst:
        assert act.stdout.find(cmd) > 0
