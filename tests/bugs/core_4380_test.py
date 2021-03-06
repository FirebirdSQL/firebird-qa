#coding:utf-8
#
# id:           bugs.core_4380
# title:        ISQL truncates blob when reading an empty segment
# decription:   
#                  Checked on: 4.0.0.138 (both Windows and POSIX); 3.0.0.32484.
#                
# tracker_id:   CORE-4380
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    create procedure sp_test_master(a_id int) returns(o_txt varchar(20)) as
    begin
    end
    ^
    set term ;^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import subprocess
#  import re
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  #    -- NB: i'm not sure that this test properly reflects the trouble described in the ticket.
#  #    -- At least on 3.0 Alpha 1, Alpha 2 and Beta 2 (31807) output is identical.
#  #    -- Note that value in "BLR to Source mapping" under 'Column' was changed to reflect
#  #    -- real offset from the beginning of line in THIS .fbt file (right shifted on 4 character).
#  
#  sql_script='''  set blob all;
#    set list on;
#    select rdb$debug_info from rdb$procedures;
#  '''
#  
#  f_blob_sql = open( os.path.join(context['temp_directory'],'tmp_blob_4380.sql'), 'w')
#  f_blob_sql.write(sql_script)
#  f_blob_sql.close()
#  
#  f_blob_log = open( os.path.join(context['temp_directory'],'tmp_blob_4380.log'), 'w')
#  
#  subprocess.call( [ context['isql_path'], dsn, "-i", f_blob_sql.name],
#                   stdout = f_blob_log,
#                   stderr = subprocess.STDOUT
#                 )
#  f_blob_log.close()
#  
#  # RDB$DEBUG_INFO                  1a:1e1
#  #        Parameters:
#  #            Number Name                             Type
#  #        --------------------------------------------------
#  #                 0 A_ID                             INPUT
#  #                 0 O_TXT                            OUTPUT
#  #
#  #        Variables:
#  #            Number Name
#  #        -------------------------------------------
#  #                 0 O_TXT
#  #
#  #        BLR to Source mapping:
#  #        BLR offset       Line     Column
#  #        --------------------------------
#  #                42          2         79
#  #                ^           ^          ^
#  #                |           |          |
#  #                +-----------+----------+---- all of them can vary!
#  
#  # Print content of log with filtering lines:we are interesting only for rows
#  # which contain words: {'Parameters', 'Number', 'Variables', 'BLR'}.
#  # For last line (with three numbers for offset, line and col) we just check
#  # matching of row to appropriate pattern.
#  
#  # NB: we remove all exsessive spaces from printed lines.
#  
#  pattern = re.compile("[\\s]+[0-9]+[\\s]+[0-9]+[\\s]+[0-9]+")
#  
#  with open( f_blob_log.name,'r') as f:
#      for line in f:
#          line = line.upper()
#  
#          if ('PARAMETER' in line or
#             'NUMBER' in line or
#             'INPUT' in line or
#             'OUTPUT' in line or
#             'VARIABLE' in line or
#             'BLR' in line):
#              print(' '.join(line.split()).upper())
#  
#          if pattern.match(line):
#              print('VALUES: <OFFSET> <LINE> <COLUMN>')
#  
#  ################################################
#  # Cleanup
#  
#  f_list=[]
#  f_list.append(f_blob_sql)
#  f_list.append(f_blob_log)
#  
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i].name):
#          os.remove(f_list[i].name)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PARAMETERS:
    NUMBER NAME TYPE
    0 A_ID INPUT
    0 O_TXT OUTPUT
    VARIABLES:
    NUMBER NAME
    BLR TO SOURCE MAPPING:
    BLR OFFSET LINE COLUMN
    VALUES: <OFFSET> <LINE> <COLUMN>
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


