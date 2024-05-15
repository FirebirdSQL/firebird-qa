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
FBTEST:      bugs.core_5470
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

ddl_lst = ["""recreate /* ddl_1 line_1 */

            table /* ddl_1 line_2 */



            t_test /* ddl_1 line_3 */ (x int)
        """,
           """comment on  /* ddl_2 line_1 */
    table /* ddl_2 line_2 */


    t_test is /* ddl_2 line_3 */
            'foo  /* ddl_2 line_4 */
             /* ddl_2 line_4 */ bar'
    """,
"""

            create /* ddl_3 line_1 */
    or /* ddl_3 line_2 */

    alter /* ddl_3 line_3 */
                    view /* ddl_3 line_4 */

                    v_rio /* ddl_3 line_5 */

                    as /* ddl_3 line_6 */
                    select * /* ddl_3 line_6 */
                    from /* ddl_3 line_7 */

                    rdb$database /* ddl_3 line_8 */
    """]

trace = ['time_threshold = 0',
         'log_initfini = false',
         'log_errors = true',
         'log_statement_finish = true',
         #'include_filter = "%(recreate|create|alter|drop|comment on)[[:WHITESPACE:]]+(domain|generator|sequence|exception|procedure|function|table|index|view|trigger|role|filter|external function)%"',
         'include_filter = "%(ddl_[[:DIGIT:]]+[[:WHITESPACE:]]+line_[[:DIGIT:]]+)%"',
         ]

@pytest.mark.trace
@pytest.mark.version('>=3')
def test_1(act: Action, capsys):
    with act.trace(db_events=trace), act.db.connect() as con:
        for cmd in ddl_lst:
            con.execute_immediate(cmd)
        con.commit()

    #print(act.trace_to_stdout())
    print(act.trace_log)
    act.expected_stdout = '' # expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    
    # Check
    #act.trace_to_stdout()
    #for cmd in ddl_lst:
    #    assert act.stdout.find(cmd) > 0
