#coding:utf-8
#
# id:           functional.tabloid.loose_record_when_relief_where_expr
# title:        Uncomment of one part of OR'ed expression led to loose of record from resultset.
# decription:   
#                   "OR" could __reduce__ number of rows in resultset.
#                   See leters to/from dimitr 23.09.2010 (probably this bug was due to occasional typo).
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
     set list on;
     with
     tset_init as
     (
         select
             61844284 srvt_id
             ,n.row_id
         from
         rdb$database lcat
         left join (
             select 1 row_id from rdb$database 
             union all select 2 from rdb$database
         ) n on 1=1
     )
     ,t_separate as
     (
         select
             srvt_id
             ,row_id
             ,v.c selected_case
         from tset_init
         join (
             select 'A' c from rdb$database 
             union all 
             select 'B' from rdb$database
         ) v
         on
         v.c='A'
         -- One record DISappeared from resultset when this part 
         -- of OR'ed expression was UNcommented.
         or v.c='B' and srvt_id=0 -- 2.5.0, /src/jrd/opt.cpp, line 4228: for (UCHAR i = 1; i <= streams[0]; i++)
     )
     select t.* from t_separate t
     ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SRVT_ID                         61844284
    ROW_ID                          1
    SELECTED_CASE                   A
    SRVT_ID                         61844284
    ROW_ID                          2
    SELECTED_CASE                   A
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

