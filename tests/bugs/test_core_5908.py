#coding:utf-8
#
# id:           bugs.core_5908
# title:        Enhance dynamic libraries loading related error messages
# decription:   
#                  We intentionally try to load unit from non-existent UDR module with name "udrcpp_foo".
#                  Message 'module not found' issued BEFORE fix - without any detalization.
#                  Current output should contain phrase: 'UDR module not loaded'.
#                  Filtering is used for prevent output of localized message about missed UDR library.
#               
#                  Checked on:
#                      3.0.4.33053: OK, 13.968s.
#                      4.0.0.1210: OK, 2.375s.
#                  Thanks to Alex for suggestion about test implementation.
#                
# tracker_id:   CORE-5908
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import re
#  
#  udr_sp_ddl='''
#      create or alter procedure gen_foo2 (
#          start_n integer not null,
#          end_n integer not null
#      ) returns( n integer not null )
#          external name 'udrcpp_foo!gen_rows'
#          engine udr
#  '''
#  
#  allowed_patterns = (
#       re.compile('\\.*module\\s+not\\s+(found|loaded)\\.*', re.IGNORECASE),
#  )
#  
#  try:
#      db_conn.execute_immediate( udr_sp_ddl )
#      db_conn.commit() # --------------------- this will fail with message about missed UDR livrary file.
#  except Exception,e:
#      ##############################################################################
#      # We parse exception object and allow for output only such lines from it
#      # that relate to missed MODULE, and no other text (localization can be here!):
#      ##############################################################################
#      for i in e[0].split('\\n'):
#          match2some = filter( None, [ p.search(i) for p in allowed_patterns ] )
#          if match2some:
#              print( (' '.join(i.split()).upper()) )
#  finally:
#      db_conn.close()
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    - UDR MODULE NOT LOADED
  """

@pytest.mark.version('>=3.0.4')
@pytest.mark.xfail
def test_core_5908_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


