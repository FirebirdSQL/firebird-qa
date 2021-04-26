#coding:utf-8
#
# id:           bugs.core_5277
# title:        Parameters with multibyte character sets allow to bypass the character limit of varchar fields
# decription:   
#                  Checked on LI-V3.0.1.32533, built it from sources 20160617 19:30
#                
# tracker_id:   CORE-5277
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = [('BULK>.*', '')]

init_script_1 = """
    recreate table test ( c varchar(2) character set utf8 );
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  # 'connection_character_set': 'UTF8',
#  
#  db_conn.close()
#  
#  sql_chk='''   
#      set bulk_insert insert into test values(?);
#      ('ab')
#      ('qw')
#      ('er')
#      ('tyu')
#      stop
#      set list on; -- !! do NOT remove this "duplicate" statement, otherwise data will be shown as when set list OFF !! Incredible... 8-O
#      set list on;
#      select * from test;
#  
#      commit;
#      -----------------------------------
#      -- Following sample was discussed with dimitr 29.06.2016.
#      -- Statement failed, SQLSTATE = 22001
#      -- arithmetic exception, numeric overflow, or string truncation
#      -- -string right truncation
#      -- -expected length 10, actual 17
#      set term ^;
#      create or alter function get_mnemonic (
#          afield_name type of column rdb$types.rdb$field_name,
#          atype type of column rdb$types.rdb$type)
#      returns type of column rdb$types.rdb$type_name 
#      as
#      begin
#        return (select rdb$type_name
#                from rdb$types
#                where
#                    rdb$field_name = :afield_name
#                    and rdb$type = :atype
#                order by rdb$type_name
#               );
#      end
#      ^
#      set term ;^
#      commit;
#  
#      set list on;
#  
#      select get_mnemonic('MON$SHUTDOWN_MODE', 1) as mnemonic from rdb$database;
#  '''
#  
#  runProgram('isql',[dsn, '-ch', 'utf8'],sql_chk)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    C                               ab
    C                               qw
    C                               er
    MNEMONIC                        MULTI_USER_SHUTDOWN
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22001
    arithmetic exception, numeric overflow, or string truncation
    -string right truncation
    -expected length 2, actual 3
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 1, column 1
    -stop
  """

@pytest.mark.version('>=3.0.1')
@pytest.mark.xfail
def test_core_5277_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


