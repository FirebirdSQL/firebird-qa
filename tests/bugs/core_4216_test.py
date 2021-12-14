#coding:utf-8
#
# id:           bugs.core_4216
# title:        Memory leak with TRIGGER ON TRANSACTION COMMIT
# decription:   
#                   We create database-level trigger on COMMIT and run loop of 3000 iterations with invoking autonomous transaction.
#                   Before and after this loop we register memory_used & memory_allocated in order to compare these values after.
#                   Ratio must be close to 1.05...1.1.
#               
#                   Confirmed valuable memory leak on WI-V2.5.2.26540: memmory_used was increased for ~2.75 times after 3000 iterations.
#                       MEM_USED_RATIO       MEM_ALLOC_RATIO
#                       ============== =====================
#                               2.7671                2.0729
#               
#                   FB25SC, build 2.5.8.27090: OK, 2.078s.
#                   FB30SS, build 3.0.3.32901: OK, 3.063s.
#                   FB40SS, build 4.0.0.875: OK, 3.704s.
#                
# tracker_id:   CORE-4216
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;

    recreate view v_memo as select 1 i from rdb$database;
    commit;

    set term ^;
    create or alter trigger trg_commit inactive on transaction commit as
        declare c smallint;
    begin
        select rdb$relation_id from rdb$relations order by rdb$relation_id desc rows 1 into c;
    end
    ^
    execute block as
    begin
      execute statement 'drop sequence g';
      when any do begin end
    end
    ^
    set term ;^
    commit;

    create sequence g;
    commit;

    recreate view v_memo as
    select
        cast( gen_id(g,1) as smallint) as sn,
        cast( mon$stat_id as int) as stat_id,
        cast( mon$stat_group as int)  as stat_gr,
        cast( mon$memory_used as int)  as mem_used,
        cast( mon$memory_allocated as int)  as mem_alloc
    from mon$memory_usage
    where mon$memory_used = (select max(mon$memory_used) from mon$memory_usage)
    ;
    commit;

    recreate table tlog(sn smallint, stat_id int, stat_gr int, mem_used int, mem_alloc int);
    commit;

    alter trigger trg_commit active;
    commit;
    --------------------------------------

    insert into tlog select * from v_memo;
    commit;

    set term ^;
    execute block as
        declare n int = 3000;
    begin
        while ( n > 0 ) do
            in autonomous transaction do
                select :n - 1 from rdb$database into n;
    end
    ^
    set term ;^

    insert into tlog select * from v_memo;
    commit;

    -- select * from tlog;
    set list on;
    select 
         iif( mem_used_ratio < max_allowed_ratio, 'OK, acceptable.', 'BAD ratio of mem_used: ' || mem_used_ratio || ' - exceeds threshold = ' || max_allowed_ratio) as mem_used_ratio
        ,iif( mem_alloc_ratio < max_allowed_ratio, 'OK, acceptable.', 'BAD ratio of mem_alloc: ' || mem_alloc_ratio || ' - exceeds threshold = ' || max_allowed_ratio ) as mem_alloc_ratio
    from (
        select 
            --max(iif(sn=1, mem_used,0)) mu_1 
            --,max(iif(sn=2, mem_used,0)) mu_2
            --,max(iif(sn=1, mem_alloc,0)) ma_1 
            --,max(iif(sn=2, mem_alloc,0)) ma_2
             cast( 1.0000 * max(iif(sn=2, mem_used,0)) / max(iif(sn=1, mem_used,0)) as numeric(12,4) ) mem_used_ratio
            ,cast( 1.0000 * max(iif(sn=2, mem_alloc,0)) / max(iif(sn=1, mem_alloc,0)) as numeric(12,4) ) mem_alloc_ratio
            ,1.10 as max_allowed_ratio
            --            ^
            -- ##########################
            -- ### T H R E S H O L D  ###
            -- ##########################
        from tlog
    )
    ;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MEM_USED_RATIO                  OK, acceptable.
    MEM_ALLOC_RATIO                 OK, acceptable.
  """

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout
