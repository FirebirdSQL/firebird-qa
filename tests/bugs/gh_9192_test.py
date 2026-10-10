#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9192
TITLE:       ORDER BY in window function causes slowdown because the frame is evaluated for every row ...
DESCRIPTION:
    Test measures CPU time that is spent for loop of <N_MEASURES> iterations, in each of which we run several queries from ticket.
    The first query is called here as `ANCHOR` and is `select` that does not use window function (but runs SORT causes by `ORDER BY`).
    Median value of of CPU time for this query has name `anchor_cpu_time` and appropriate median values for subsequent queries will be
    divided on this `anchor_cpu_time` and then be compared with thresholds.
    For each query we assign `individual` threshold, see `qry_map[key][1]`.

    Test is considered as passed if median ratios for *all* queries (except `anchor`) are less than appropriate thresholds.
NOTES:
    [10.10.2026] pzotov.
    The initial DDL was taken from ticket but number of rows reduced (it appears enough top have about 50K rows in the test table).
    Before fix ratio between median CPU times was 4.33 ... 4.67. After fix it became ~2.33 ... 2.67
    
    Confirmed problem on 6.0.0.2199-bf94598.
    Checked on 6.0.0.2204-2d20c77.
"""
from statistics import median
import psutil
import pytest
from firebird.qa import *

###########################
###   S E T T I N G S   ###
###########################
NUM_ROWS = 50000
N_MEASURES = 5

init_script = f"""
    create table test (
        id integer not null primary key,
        k integer,
        d date,
        v numeric(15,2)
    );
    commit;

    set term ^;
    execute block as
      declare i int = 1;
    begin
      while (i <= {NUM_ROWS}) do
      begin
        insert into test (id, k, d, v)
        values (
            :i
            ,mod(:i * 7919, 10000)
            ,dateadd(mod(:i * 31, 2000) day to date '2020-01-01')
            ,mod(:i * 13, {NUM_ROWS}) / 100.00
        );
        i = i + 1;
      end
    end^
    set term ;^
    commit;
"""

db = db_factory(init = init_script)
act = python_act('db')

@pytest.mark.perf_measure
@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    ANCHOR_IDX = 1000
    
    with act.db.connect() as con:
        cur=con.cursor()
        cur.execute('select mon$server_pid as p from mon$attachments where mon$attachment_id = current_connection')
        fb_pid = int(cur.fetchone()[0])

        times_map = {}
        t_medians = {}

        # indices in values tuple: 0 = query; 1 = threshold
        qry_map = {
            ANCHOR_IDX : ( 'select count(*) from (select id from test order by k, d, id) x', 1 )
           ,2000 : ( 'select count(*) from (select row_number()over(partition by k order by d, id) w from test) x', 3 )
           ,3000 : ( 'select count(*) from (select lag(id)over(partition by k order by d, id) w from test) x', 3.5 )
           ,4000 : ( 'select count(*) from (select ntile(4)over(partition by k order by d, id) w from test) x', 3.5 )
           ,5000 : ( 'select count(*) from (select sum(v) over (partition by k order by d, id rows between unbounded preceding and current row) w from test) x', 4 )
        }
       
        for k,v in qry_map.items():
            qry_sql = v[0]
            ps = cur.prepare(qry_sql)
            for i in range(N_MEASURES):
                fb_cpu_0 = psutil.Process(fb_pid).cpu_times()
                cur.execute(ps)
                for r in cur:
                    pass
                fb_cpu_1 = psutil.Process(fb_pid).cpu_times()
                times_map[ k, i ]  = max(fb_cpu_1.user - fb_cpu_0.user, 0.000001)
            
            t_medians [ k ] = median( [v for kx,v in times_map.items() if kx[0] == k] )


    k_denom = ANCHOR_IDX
    anchor_cpu_time = t_medians[ k_denom ]
    all_fine = 1
    expected_lst = []
    for k,v in t_medians.items():
        if k != k_denom:
            max_ratio_to_anchor = qry_map[k][1]
            if v / anchor_cpu_time > max_ratio_to_anchor:
                all_fine = 0
            msg_prefix = 'ratio between medians of CPU time:'
            
            print(qry_map[k][0])
            print(msg_prefix, 'acceptable' if v / anchor_cpu_time <= max_ratio_to_anchor else f'TOO BIG: {v / anchor_cpu_time : .4f} - greater than {max_ratio_to_anchor : .4f}')

            expected_lst.append( '\n'.join((qry_map[k][0], msg_prefix + ' acceptable')) )

    if all_fine:
        pass
    else:
        print(f'anchor_cpu_time = {anchor_cpu_time:.4f}')
        print('t_medians:')
        for k,v in t_medians.items():
            print(qry_map[k][0], f' : median CPU-time={v:.4f}, ratio to anchor_cpu_time: {v/anchor_cpu_time:.4f}')

    act.expected_stdout = '\n'.join( expected_lst )
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
