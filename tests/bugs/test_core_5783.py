#coding:utf-8
#
# id:           bugs.core_5783
# title:        execute statement ignores the text of the SQL-query after a comment of the form "-"
# decription:   
#                  We concatenate query from several elements and use '
#               ' delimiter only to split this query into lines.
#                  Also, we put single-line comment in SEPARATE line between 'select' and column/value that is obtained from DB.
#                  Final query will lokk like this (lines are separated only by SINGLE delimiter, ascii_char(13), NO '
#               ' here!):
#                  ===
#                      select
#                      -- comment N1
#                      'foo' as msg'
#                      from
#                      -- comment N2
#                      rdb$database
#                  ===
#                  This query should NOT raise any exception and must produce normal output (string 'foo').
#                  Thanks to hvlad for suggestions.
#               
#                  Confirmed bug on:
#                      3.0.4.32924
#                      4.0.0.918
#                  -- got:
#                      Error while preparing SQL statement:
#                      - SQLCODE: -104
#                      - Dynamic SQL Error
#                      - SQL error code = -104
#                      - Unexpected end of command - line 1, column 1
#                      -104
#                      335544569
#                  Checked on:
#                      3.0.4.32941: OK, 1.187s.
#                      4.0.0.947: OK, 1.328s.
#                
# tracker_id:   CORE-5783
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
# import sys
#  import os
#  
#  cur = db_conn.cursor()
#  
#  # NB: one need to use TWO backslash characters ('\\r') as escape for CR only within fbtest. 
#  # Single '' should be used when running under "pure" Python control:
#  
#  sql_expr = ' '.join( ('select', '\\r', '-- comment N1', '\\r', "'foo' as msg", '\\r', 'from', '\\r', '-- comment N2', '\\r', 'rdb$database') )
#  
#  for i in sql_expr.split('\\r'):
#      print('Query line: ' + i)
#  
#  #sql_expr = 'select 1 FROM test'
#  cur.execute( sql_expr )
#  for r in cur:
#      print( 'Query result: ' + r[0] )
#  
#  cur.close()
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Query line: select
    Query line:  -- comment N1
    Query line:  'foo' as msg
    Query line:  from
    Query line:  -- comment N2
    Query line:  rdb$database
    Query result: foo
  """

@pytest.mark.version('>=3.0.4')
@pytest.mark.xfail
def test_core_5783_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


