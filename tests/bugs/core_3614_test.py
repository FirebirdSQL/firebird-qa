#coding:utf-8
#
# id:           bugs.core_3614
# title:        Plan returned for query with recursive CTE return wrong count of parenthesis
# decription:   
#                
# tracker_id:   CORE-3614
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test_tree(
        id integer not null,
        id_header integer,
        constraint pk_test_tree__id primary key (id)
    );

    create index ixa_test_tree__id_header on test_tree (id_header);
    commit;

    insert into test_tree values ('1', null);
    insert into test_tree values ('2', null);
    insert into test_tree values ('3', null);
    insert into test_tree values ('4', '1');
    insert into test_tree values ('5', '4');
    insert into test_tree values ('6', '2');
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import subprocess
#  import time
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  #---------------------------------------------
#  
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f, 
#      # first do f.flush(), and 
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#      
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#              if os.path.isfile( f_names_list[i]):
#                  print('ERROR: can not remove file ' + f_names_list[i])
#  
#  #--------------------------------------------
#  
#  sql='''
#      set planonly;
#      with recursive
#      r_tree as
#      (
#          select tt.id as a, cast(tt.id as varchar(100)) as asum
#          from test_tree tt
#          where tt.id_header is null
#  
#          union all
#           
#          select tt.id as a, rt.asum || '_' || tt.id
#          from test_tree tt join r_tree rt on rt.a = tt.id_header
#      )
#      select *
#      from r_tree rt2  join test_tree tt2 on tt2.id=rt2.a
#      ;
#  '''
#  f_isql_cmd=open( os.path.join(context['temp_directory'],'tmp_isql_3614.sql'), 'w')
#  f_isql_cmd.write(sql)
#  flush_and_close( f_isql_cmd )
#  
#  f_isql_log=open( os.path.join(context['temp_directory'],'tmp_isql_3614.log'), 'w')
#  
#  subprocess.call( [ context['isql_path'], dsn, '-i', f_isql_cmd.name], stdout=f_isql_log, stderr=subprocess.STDOUT)
#  
#  flush_and_close( f_isql_log	)
#  
#  # Let buffer be flushed on disk before we open log and parse it:
#  time.sleep(1)
#  
#  # For every line which contains word 'PLAN' we count number of '(' and ')' occurences: they must be equal.
#  # We display difference only when it is not so, thus 'expected_stdout' section must be EMPTY.
#  with open( f_isql_log.name,'r') as f:
#      for line in f:
#          if 'PLAN' in line and line.count( '(' ) - line.count( ')' ) != 0:
#              print(  'Difference in opening vs close parenthesis: ' + str( line.count( '(' ) - line.count( ')' ) )  )
#  
#  cleanup( [i.name for i in (f_isql_cmd, f_isql_log)] )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


