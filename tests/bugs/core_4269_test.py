#coding:utf-8
#
# id:           bugs.core_4269
# title:        Wrong output when field with result of windowed function is used in query with useless WHERE 0=0 and GROUP BY clause
# decription:   
# tracker_id:   CORE-4269
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table tb_a(q int, v int); commit;
    insert into tb_a
    with
    x as(
      select 1 q, 1 v from rdb$database union all
      select 1 q, 7 v from rdb$database
    )
    select * from x;
    commit;
    recreate table tv_a(v int, n varchar(10), c varchar(10) ); commit;
    insert into tv_a
    with
    x as(
      select 1 v, 'a1' n, 'r' c from rdb$database union all
      select 7 v, 'a7' n, 'b' c from rdb$database
    )
    select * from x;
    commit; 
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select c.rdb$character_set_name as connection_cset, r.rdb$character_set_name as db_default_cset
    from mon$attachments a
    join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
    cross join rdb$database r where a.mon$attachment_id=current_connection;
    with
    tc as(
        select
            tb_a.q, tb_a.v, tv_a.c,
            dense_rank () over (partition by tv_a.c order by tb_a.v) rk,
            case when tv_a.c = 'r' then tv_a.n end r
        from tb_a
        join tv_a on tv_a.v = tb_a.v
        where tb_a.q=1
    )
    
    select q, rk , max(r) as max_r
    from tc
    where 0=0
    group by q, rk
    
    UNION ALL
    
    select q, rk , max(r)
    from tc
    group by q, rk;
    set list off;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
CONNECTION_CSET                 UTF8
DB_DEFAULT_CSET                 UTF8
Q                               1
RK                              1
MAX_R                           a1
Q                               1
RK                              1
MAX_R                           a1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

