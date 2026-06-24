#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8661
TITLE:       Strange output from SHOW DEPENDENCIES command on 6.0
NOTES:
    [23.07.2025] pzotov
        Presense of several VIEWS that depend on table <T> caused weird output of command 'show depend <T>'.
        Confirmed bug (several excessive lines like '[PUBLIC.TEST:Table]' after first one) on 6.0.0.1050-cee7854.
        Checked on 6.0.0.1052-c6658eb; 5.0.3.1684; 4.0.6.3222; 3.0.13.33818
    [09.10.2025] pzotov
        Adjusted output for 6.x after 3e3b75 ("Re-add indexes for object name without schema name...")
        Checked on 6.0.0.1299
    [25.06.2026] pzotov
        The order of objects in 'SHOW DEPEND' output has changed since 6.0.0.1806 2026.03.01 72cd2 (shared metadata cache):
        now it looks similar to previous FB versions: 'OBJECT_NAME_i, CHILD_OBJECT_NAME_i' etc:
            - PUBLIC.V_TEST1:View, PUBLIC.V_TEST2:View, ..., PUBLIC.V_TEST1:View->ID, PUBLIC.V_TEST2:View->ID, ...
            + PUBLIC.V_TEST1:View, PUBLIC.V_TEST1:View->ID, PUBLIC.V_TEST2:View, PUBLIC.V_TEST2:View->ID, ...
        Because every SHOW-command in ISQL has extremely 'fragile' output, it was decided to analyze ordered list of tokens
        that are result of SPLIT lines call. We may restrict parsing only for lines that contain ':view' or ':table' phrases.
        Checked on 6.0.0.2028; 5.0.5.1837; 4.0.8.3286; 3.0.15.33867
"""

import pytest
from firebird.qa import *

init_script = """
    create table test(id int primary key);
    create view v_test1 as select id from test;
    create view v_test2 as select id from test;
    create view v_test3 as select id from test;
    create view v_test4 as select id from test;
    create view v_test5 as select id from test;
    commit;
"""
db = db_factory(init = init_script)

test_script = """
    show depen test;
"""

act = python_act('db')

expected_stdout_5x = """
    V_TEST1:View
    V_TEST1:View->ID
    V_TEST2:View
    V_TEST2:View->ID
    V_TEST3:View
    V_TEST3:View->ID
    V_TEST4:View
    V_TEST4:View->ID
    V_TEST5:View
    V_TEST5:View->ID
    [TEST:Table]
"""

expected_stdout_6x = """
    PUBLIC.V_TEST1:View
    PUBLIC.V_TEST1:View->ID
    PUBLIC.V_TEST2:View
    PUBLIC.V_TEST2:View->ID
    PUBLIC.V_TEST3:View
    PUBLIC.V_TEST3:View->ID
    PUBLIC.V_TEST4:View
    PUBLIC.V_TEST4:View->ID
    PUBLIC.V_TEST5:View
    PUBLIC.V_TEST5:View->ID
    [PUBLIC.TEST:Table]
"""

@pytest.mark.version('>=3.0.13')
def test_1(act: Action, capsys):
    
    act.isql(switches = ['-q'], input = 'show depen test;', combine_output = True)
    depend_lst = []
    for line in act.clean_stdout.splitlines():
        depend_lst.extend( [ x.strip() for x in line.split(',') if ':view' in x.lower() or ':table' in x.lower() ] )
    act.reset()
    for p in sorted(depend_lst):
        print(p)
    act.stdout = capsys.readouterr().out
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    assert act.clean_stdout == act.clean_expected_stdout
