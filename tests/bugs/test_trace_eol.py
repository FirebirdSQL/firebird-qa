#coding:utf-8

"""
ID:          issue-5740
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/5740
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

chk_statements_lst = ["""recreate /* ddl_1 line_1 */

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
         'max_sql_length = 65500',
         'include_filter = "%(ddl_[[:DIGIT:]]+[[:WHITESPACE:]]+line_[[:DIGIT:]]+)%"',
         ]

@pytest.mark.trace
@pytest.mark.version('>=3.0.2')
def test_1(act: Action, capsys):
    with act.trace(db_events=trace), act.db.connect() as con:
        for cmd in chk_statements_lst:
            con.execute_immediate(cmd)
        con.commit()

    trace_txt = '\n'.join( [line.rstrip() for line in act.trace_log] )
    missed_cnt = 0
    for sttm in [c.rstrip() for c in chk_statements_lst]:
        if trace_txt.find(sttm) < 0:
            missed_cnt += 1
            if missed_cnt == 1:
                print('Missed in the trace log:')
            
            print('----- sttm start -----')
            for x in [x.strip() for x in sttm.split('\n')]:
                print(x)
            print('----- sttm finish ----')
    
    if missed_cnt:
        print('----- trace start -----')
        for x in trace_txt.split('\n'):
            print(x)
        print('----- trace finish ----')


    '''
    all_found = True
    act.trace_to_stdout()
    for cmd in chk_statements_lst:
        #if act.stdout.find(cmd) <= 0:
        #    all_found = False
        #    print(f'{cmd=}')
        #    print(f'{act.stdout=}')
        #    print(f'{act.trace_log=}')
        #    break
    #    assert act.stdout.find(cmd) > 0
    print(f'{all_found=}')
    '''

    act.expected_stdout = '' # expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
