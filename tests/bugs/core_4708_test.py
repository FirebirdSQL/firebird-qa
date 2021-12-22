#coding:utf-8
#
# id:           bugs.core_4708
# title:        Content of MON$EXPLAINED_PLAN in MON$STATEMENTS is truncated if exceeds the 32KB limit
# decription:   
# tracker_id:   CORE-4708
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('MON_EXPLAINED_PLAN_TAIL.*', 'MON_EXPLAINED_PLAN_TAIL')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set blob all;
    -- This query has explained plan with length ~47 Kb (checked on WI-V3.0.0.32253).
    -- Instead of checking explained plan text it is enough only to ensure that its 
    -- LENGTH is more than 32K and that text is not cuted off, i.e. it should end with
    -- phrase: Table "MON$STATEMENTS" Full Scan
    -- Another sample of query that has long plan see in core_5061.fbt
    with recursive
    rx as (
      select 1 as i from rdb$database
      union all
      select r.i+1 from rx r where r.i < 2
    )
    ,r2 as (
      select row_number() over() i 
      from rx r 
      full join rx r2 on r2.i=r.i 
      group by r.i 
      having count(*)>0 
      order by r.i rows 1
    )
    select
         iif( char_length(mon$explained_plan) > 32767, 'MORE THAN 32K', 'LESS THEN 32K' ) as mon_explained_plan_len
        ,right(mon$explained_plan,32) as mon_explained_plan_tail
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)

        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)

        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        ,(select count(*) from r2)
        --,(select count(*) from r2)
    from mon$statements s
    where 
    s.mon$attachment_id = current_connection
    -- 08-may-2017: need for 4.0 Classic! 
    -- Currently there is also query with RDB$AUTH_MAPPING data in mon$statements:
    and s.mon$sql_text containing 'select 1 as i'
    ;
    -- Table "MON$STATEMENTS" Full Scan
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MON_EXPLAINED_PLAN_LEN          MORE THAN 32K
    MON_EXPLAINED_PLAN_TAIL         0:4
    MON$STATEMENTS" as "S" Full Scan
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
    COUNT                           1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

