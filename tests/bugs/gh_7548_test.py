#coding:utf-8

"""
ID:          issue-7548
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7548
TITLE:       SET BIND OF TIMESTAMP WITH TIME ZONE TO CHAR is not working with UTF8 connection charset
DESCRIPTION:
    Test checks all character sets defined in CHARSET_MAP dictionary (see firebird/driver/core.py).
    No errors must occur for all of them.
NOTES:
    [19.04.2023] pzotov
    Confirmed bug on 4.0.3.2930, 5.0.0.1017
    Checked on 4.0.3.2931, 5.0.0.1021 - all OK.
"""

import pytest
from firebird.qa import *
from firebird.driver import CHARSET_MAP

db = db_factory()

ts = '19-APR-2023 21:15:19.0110'
test_sql = f"""
    set list on;
    recreate table test(f01 timestamp with time zone);
    insert into test values(timestamp '{ts}');
    set term ^;
    execute block as
    begin
        set bind of timestamp with time zone to char;
    end
    ^
    set term ;^
    select * from test;
    commit;
"""

substitutions = [ ('[\t ]+', ' '), (f'F01 {ts} .*', f'F01 {ts}') ]

act = python_act('db', substitutions = substitutions)

expected_stdout = f"""
    F01 {ts} Europe/Moscow
"""

@pytest.mark.version('>=4.0.3')
def test_1(act: Action, capsys):
    cset_list = []
    with act.db.connect() as con:
        with con.cursor() as cur:
            cur.execute("select trim(c.rdb$character_set_name) from rdb$character_sets c where coalesce(c.rdb$system_flag,0)<>0 and c.rdb$character_set_name not in ('NONE', 'OCTETS')")
            cset_list = [x[0] for x in cur.fetchall() if x[0] in CHARSET_MAP]

    #print(cset_list)
    #assert '' == capsys.readouterr().out

    cset_fails = {}
    for x in cset_list:
        act.reset()
        act.expected_stdout = expected_stdout
        act.isql(switches=['-q'], charset = x, input = test_sql, combine_output = True)
        if act.clean_stdout == act.clean_expected_stdout:
            pass
        else:
            cset_fails[x] = act.clean_stdout

    if cset_fails:
        print('Detected fail for some charset(s):')
        for k,v in sorted(cset_fails.items()):
            print( f'charset: {k}' )
            print('Result:')
            for p in v.split('\n'):
                print(p)
            print('')
    
    assert '' == capsys.readouterr().out
