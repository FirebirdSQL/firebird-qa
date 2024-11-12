#coding:utf-8

"""
ID:          issue-5009
ISSUE:       5009
TITLE:       Index and blob garbage collection doesn't take into accout data in undo log [CORE4701]
DESCRIPTION:
JIRA:        CORE-4701
NOTES:
    [02.11.2024] pzotov
    Confirmed bug on 3.0.13.33794.
    Checked on 4.0.6.3165, 5.0.2.1551, 6.0.0.415
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table g_test (f integer);
    create index g_ind on g_test (f);
    insert into g_test values (1);
    commit;
    update g_test set f=2;
    savepoint a;
    update g_test set f=3;
    savepoint b;
    update g_test set f=3;
    savepoint c;
    update g_test set f=4;
    savepoint d;
    update g_test set f=4;
    release savepoint b only;
    rollback to savepoint c;
    commit;
    set list on;
    set count on;
    set plan on;

    select g.f as f_natreads from g_test g;
    
    select g.f as f_idxreads from g_test g where g.f between 1 and 4;
"""

act = isql_act('db', test_script, substitutions = [ ('[ \t]+', ' '), ])

@pytest.mark.version('>=4.0.0')
def test_1(act: Action, capsys):

    act.execute(combine_output = True)

    act.expected_stdout = """
        PLAN (G NATURAL)
        F_NATREADS 3
        Records affected: 1
        PLAN (G INDEX (G_IND))
        F_IDXREADS 3
        Records affected: 1
    """

    with act.connect_server() as srv:
        srv.database.validate(database = act.db.db_path)
        validate_err = '\n'.join( [line for line in srv if 'ERROR' in line.upper()] )

    expected_isql = 'ISQL output check: PASSED.'
    expected_onlv = 'Online validation: FAILED.'

    if act.clean_stdout == act.clean_expected_stdout:
        print(expected_isql)
    else:
        print(
            f"""
                ISQL output check: FAILED.
                Actual:
                {act.clean_stdout}
                Expected:
                {act.expected_stdout}
            """
        )

    if not validate_err:
        print(expected_onlv)
    else:
        print(
            f"""
               Online validation: FAILED.
               Actual:
                   {validate_err}
               Epsected:
                   <empty string>
            """
        )


    act.reset()
    act.expected_stdout = f"""
        {expected_isql}
        {expected_onlv}
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

