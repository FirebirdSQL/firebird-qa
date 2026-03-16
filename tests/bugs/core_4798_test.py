#coding:utf-8

"""
ID:          issue-5096
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/5096
TITLE:       Regression: MIN/MAX with a join ignores possible index navigation
DESCRIPTION:
JIRA:        CORE-4798
NOTES:
    [16.03.2026] pzotov
    Re-implemented after note by dimitr: con.info.get_table_access_stats() is invoked to obtain NR and IR values.
    Small threshold for max allowed indexed reads remains if optimizer and statistics will be changed in the future.
    Checked on 6.0.0.1824, 5.0.4.1780, 4.0.7.3256, 3.0.14.33845.
"""

import pytest
from firebird.qa import *

NAT_READS_MAX_THRESHOLD = 0
IDX_READS_MAX_THRESHOLD = 5

init_script = """
    recreate table test(x int);
    commit;
    set term ^;
    execute block as
        declare n int = 100000;
    begin
        while (n > 0) do
        begin
            insert into test(x) values(mod(:n, 123));
            n = n - 1;
        end
    end
    ^
    set term ;^
    commit;
    create index test_x on test(x);
"""
db = db_factory(init = init_script)

act = python_act('db')
EXPECTED_MSG = 'Expected.'

@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    nat_reads = idx_reads = 0
    with act.db.connect() as con:
        cur=con.cursor()
        cur.execute("select rdb$relation_id from rdb$relations where rdb$relation_name = upper('test')")
        test_rel_id = int(cur.fetchone()[0])

        for x_table in con.info.get_table_access_stats():
            if x_table.table_id == test_rel_id:
                nat_reads = -x_table.sequential if x_table.sequential else 0
                idx_reads = -x_table.indexed if x_table.indexed else 0

        cur.execute(f"select /* trace_me */ min(a.x) from test a join test b on a.x = b.x join test c on b.x = c.x")
        data = cur.fetchall()

        for x_table in con.info.get_table_access_stats():
            if x_table.table_id == test_rel_id:
                nat_reads += x_table.sequential if x_table.sequential else 0
                idx_reads += x_table.indexed if x_table.indexed else 0
    
    if nat_reads <= NAT_READS_MAX_THRESHOLD and idx_reads <= IDX_READS_MAX_THRESHOLD:
        print(EXPECTED_MSG)
    else:
        print('Unexpected values of NR and/or IR:')
        print(f'{nat_reads=}')
        print(f'{idx_reads=}')

    expected_stdout = EXPECTED_MSG

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
