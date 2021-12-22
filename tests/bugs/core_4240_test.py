#coding:utf-8
#
# id:           bugs.core_4240
# title:        Regression: recursive query in SQL query returns incorrect results if more than one branch bypass
# decription:   
# tracker_id:   CORE-4240
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('=', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    with recursive h 
    as (select 1 as code_horse, 
               2 as code_father, 
               3 as code_mother 
        from rdb$database 
        union all 
        select 2 as code_horse, 
               4 as code_father, 
               5 as code_mother 
        from rdb$database 
        union all 
        select 3 as code_horse, 
               4 as code_father, 
               5 as code_mother 
        from rdb$database 
        union all 
        select 4 as code_horse, 
               null as code_father, 
               null as code_mother 
        from rdb$database 
        union all 
        select 5 as code_horse, 
               null as code_father, 
               null as code_mother 
        from rdb$database), 
    r 
    as (select h.code_horse as code_horse, 
               h.code_father as code_father, 
               h.code_mother as code_mother, 
               cast('' as varchar(10)) as mark, 
               0 as depth 
        from h 
        where h.code_horse = 1 
        union all 
        select h.code_horse as code_horse, 
               h.code_father as code_father, 
               h.code_mother as code_mother, 
               'f' || r.mark as mark, 
               r.depth + 1 as depth 
        from r 
        join h on r.code_father = h.code_horse 
        where r.depth < 5 
        union all 
        select h.code_horse as code_horse, 
               h.code_father as code_father, 
               h.code_mother as code_mother, 
               'm' || r.mark as mark, 
               r.depth + 1 as depth 
        from r 
        join h on r.code_mother = h.code_horse 
        where r.depth < 5) 
    select * 
    from r 
    order by 1,2,3,4,5
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  CODE_HORSE  CODE_FATHER  CODE_MOTHER MARK              DEPTH 
           1            2            3                       0 
           2            4            5 f                     1 
           3            4            5 m                     1 
           4       <null>       <null> ff                    2 
           4       <null>       <null> fm                    2 
           5       <null>       <null> mf                    2 
           5       <null>       <null> mm                    2 
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

