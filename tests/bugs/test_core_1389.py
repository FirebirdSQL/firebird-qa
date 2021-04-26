#coding:utf-8
#
# id:           bugs.core_1389
# title:        Indexed MIN/MAX aggregates produce three index reads instead of the expected one indexed read
# decription:   
#                  We use API call db_info(fdb.isc_info_read_idx_count) for obtaining number of indexed reads and
#                  extract their values which are reported per table and are cumulative since start of attachment.
#                  Four statements are used for analyzing (table have all needed indexes): 
#                  * select max(x) from ...;
#                  * select x from ... order by x asc rows 1; 
#                  * select min(y) from ...;
#                  * select y from ... order by y desc rows 1; 
#               
#                  All of them must take only one indexed read.
#               
#                  Info about 'isc_info_read_idx_count':
#                      Number of indexed database reads <...>
#                      Reported per table.
#                      Calculated since the current database attachment started // CUMULATIVE!
#               
#                  See also:
#                  http://pythonhosted.org/fdb/reference.html#fdb.Connection.database_info
#               
#                  Confirmed bug on WI-V2.0.0.12724: db_info() received 3 (three) indexed reads instead of 1 for queries:
#                  'select min(...) from ...' and 'select max(...) from ...'
#                
# tracker_id:   CORE-1389
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test(x int, y int);
    commit;
    insert into test(x, y)
    select -1, 1 from (select 1 i from rdb$types rows 200) a, (select 1 i from rdb$types rows 200) b;
    commit;

    create index test_x on test(x);
    create descending index test_y on test(y);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import fdb
#  sql_get_rel_id="select rdb$relation_id from rdb$relations where trim(rdb$relation_name)=upper('test')"
#  
#  cur=db_conn.cursor()
#  cur.execute(sql_get_rel_id)
#  
#  test_rel=-1
#  for r in cur:
#    test_rel=r[0]
#  
#  sql_set=[ 
#      'select min(x) from test', 
#      'select x from test order by x rows 1',
#      'select max(y) from test', 
#      'select y from test order by y desc rows 1' 
#  ]
#  
#  v_previous_idx_counter=0
#  for i in range(0,len(sql_set)):
#     cur.execute(sql_set[i])
#     for r in cur:
#       y=r[0]
#  
#     info = db_conn.db_info(fdb.isc_info_read_idx_count)
#     # WI-V2.0.0.12724
#     for k,v_cumulative_idx_counter in info.items():
#        if k == test_rel:
#          print( 'Number of indexed reads: ' + str(v_cumulative_idx_counter - v_previous_idx_counter) )
#          v_previous_idx_counter = v_cumulative_idx_counter
#  cur.close()
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Number of indexed reads: 1
    Number of indexed reads: 1
    Number of indexed reads: 1
    Number of indexed reads: 1
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_core_1389_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


