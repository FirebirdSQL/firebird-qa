#coding:utf-8
#
# id:           bugs.core_4798
# title:        Regression: MIN/MAX with a join ignores possible index navigation
# decription:   
# tracker_id:   CORE-4798
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='mon-stat-gathering-3_0.fbk', init=init_script_1)

test_script_1 = """
    recreate table test(x int);
    commit;
    
    insert into test select rand()*100 from (select 1 i from rdb$types rows 50) a, (select 1 i from rdb$types rows 50) b;
    commit;
    create index test_x on test(x);
    commit;
    set term ^;
    execute block as
    begin
        -- ####################################
        -- S E T T I N G    T H R E S H O L D S
        -- ####################################
        rdb$set_context('USER_SESSION','NAT_READS_MAX_THRESHOLD', '0');
        rdb$set_context('USER_SESSION','IDX_READS_MAX_THRESHOLD', '20'); -- increased 27.07.2016
    end
    ^
    set term ;^
    
    alter sequence g_gather_stat restart with 0;
    execute procedure sp_truncate_stat;
    commit;
    
    execute procedure sp_gather_stat; ------- catch statistics BEFORE measured statement(s)
    commit;

    set term ^;
    execute block as
        declare v_dummy int;
    begin
        select min(a.x) from test a join test b on a.x = b.x join test c on b.x = c.x into v_dummy;
    end
    ^
    set term ;^
    execute procedure sp_gather_stat;  ------- catch statistics AFTER measured statement(s)
    commit;

    set list on;
        -- 3.0.0.31374 (Beta 1):
        --    natural_reads                   2500
        --    indexed_reads                   1839808
        -- 3.0.0.31852:
        --    natural_reads                   0
        --    indexed_reads                   6
        -- 4.0.0.313:
        --    natural_reads                   0
        --    indexed_reads                   18
    select
         iif( natural_reads <= nat_max, 'acceptable, <= ' || nat_max, 'abnormal, ' || natural_reads || ' > ' || nat_max ) as natural_reads
        ,iif( indexed_reads <= idx_max, 'acceptable, <= ' || idx_max, 'abnormal, ' || indexed_reads || ' > ' || idx_max ) as indexed_reads
    from (
        select
             v.natural_reads
            ,v.indexed_reads
            ,cast(rdb$get_context('USER_SESSION','NAT_READS_MAX_THRESHOLD') as int) nat_max
            ,cast(rdb$get_context('USER_SESSION','IDX_READS_MAX_THRESHOLD') as int) idx_max
        from v_agg_stat v
    );
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    NATURAL_READS                   acceptable, <= 0
    INDEXED_READS                   acceptable, <= 20
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

