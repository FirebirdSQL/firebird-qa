#coding:utf-8

"""
ID:          issue-6106
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/6106
TITLE:       ORDER BY on index can cause suboptimal index choices
DESCRIPTION:
JIRA:        CORE-5845
FBTEST:      bugs.core_5845
NOTES:
    [12.09.2023] pzotov
    Refactored: use firebird-driver ability to show plan (instead of call ISQL), removed hard-coded index names.
    Expected result is "accumulated" by traversing through dictionary items (see 'chk_qry_map') instead of be written beforehand.
    Added several queries provided by dimitr, letter 12-sep-2023.

    Checked on: 3.0.12.33707; 4.0.4.2986; 5.0.0.1204
"""

import pytest
from firebird.qa import *

P_KEY_IDX = "test_pk_id1_id2_id3".upper()
SINGLE_X_IDX = "test__x_only".upper()
COMPOUND_IDX = "test__id1_x".upper()

init_sql = f"""
    recreate table test
    (
        id1 int,
        id2 int,
        id3 int,
        x numeric(18,2),
        constraint pk_test primary key(id1, id2, id3) using index {P_KEY_IDX}
    );
    create index {SINGLE_X_IDX} on test(x);
    create index {COMPOUND_IDX} on test(id1, x);
    commit;
"""

chk_qry_map = {
     "select * from test t where t.id1=1 and t.x>0"                                : f"PLAN (T INDEX ({COMPOUND_IDX}))"
    ,"select * from test t where t.id1=1 and t.x>0 order by t.id1, t.id2, t.id3"   : f"PLAN SORT (T INDEX ({COMPOUND_IDX}))"
    ,"select * from test t where t.id1=1 and t.x>0 order by t.id1+0, t.id2, t.id3" : f"PLAN SORT (T INDEX ({COMPOUND_IDX}))"
    # following examples were provided by dimitr, 12-sep-2023:
    ,"select * from test t where t.id1 = 1 and t.x > 0 and t.id2 = 0"              : f"PLAN (T INDEX ({COMPOUND_IDX}))"
    ,"select * from test t where t.id1 = 1 and t.x = 0"                            : f"PLAN (T INDEX ({COMPOUND_IDX}))"
    ,"select * from test t where t.id1 = 1 and t.id2 = 2"                          : f"PLAN (T INDEX ({P_KEY_IDX}))"
    ,"select * from test t where t.id1 = 1 and t.id2 = 2 and t.id3 = 3"            : f"PLAN (T INDEX ({P_KEY_IDX}))"
    ,"select * from test t where t.id1 = 1 and t.x = 0 and t.id2 = 0"              : f"PLAN (T INDEX ({COMPOUND_IDX}))"
}

db = db_factory(init = init_sql)

act = python_act('db')

@pytest.mark.version('>=3.0.4')
def test_1(act: Action, capsys):

    expected_plans_lst = [ '\n'.join((k,v)) for k,v in chk_qry_map.items() ]
    with act.db.connect() as con:
        cur = con.cursor()
        for q in chk_qry_map.keys():
            ps = cur.prepare(q)
            print( q )
            print( ps.plan )
    
    act.expected_stdout = '\n'.join(expected_plans_lst)
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
