#coding:utf-8
#
# id:           bugs.core_6403
# title:        Some PSQL statements may lead to exceptions report wrong line/column
# decription:   
#                   We make list of strings, each of them is a multi-line statement starting with 'EXECUTE BLOCK ...'.
#                   Inside every EB one of following loops is checked:
#                       * while (<expr>) do ...
#                       * for select <expr> into ...
#                   -- where <expr> uses several arguments (because of loop) and eventually fails with zero division.
#                   In the BEGIN ... END block we have several lines of code which operates with arguments (see ticket examples).
#                   When <expr> fails then we catch error stack and parse it by searching line '- At block line: N, col: C'.
#                   These values (N and C) are compared later with those which are expected.
#               
#                   In order to proper evaluate expected values of (N,C) we split source expression onto separate lines and numerate them.
#                   Also, within each line we search special marker: "/*!*/" (without qoutes).
#                   If line contains this marker then we find its position and subtract 5 from it (this is length of "while" word).
#                   NB: this requer that betwee "for" and "/*!*/" we must put two space characters (see below).
#               
#                   Finally, we compare values in two dictionaries:
#                       source_expr_positions_map  - K = sequential number of exprerssion in the "main list"; V = line/col of token that causes problem;
#                       actual_stack_positions_map - K = the same as in source_expr_positions_map; V = line/col values that were parsed from error stack.
#                   All pairs for apropriate expressions must be equal.
#               
#                   If some difference will be found then we show this error stack, expected line/col coordinates and actual ones, as in this example:
#                   ==================
#                       3 UNEXPECTED MISMATCH between expected and actual values of line/col:
#                       * expected (position of problematic token): 6, 5
#                       * actual (result of error message parsing): 10, 9
#                       * source message of error:
#                       Error while executing SQL statement:
#                       - SQLCODE: -802
#                       - arithmetic exception, numeric overflow, or string truncation
#                       - Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
#                       - At block line: 10, col: 9
#                       Expression:
#                       ....:....1....:....2....:....3....:....4....:....5....:....6....:....7....:....8
#                       : 12345678901234567890123456789012345678901234567890123456789012345678901234567890
#                       1 : execute block
#                       2 : as
#                       3 :     declare n int = 5;
#                       4 :     declare c int;
#                       5 : begin
#                       6 :     for  /*!*/ select 100/:n from rdb$types into c
#                       7 :     -- ^^ NB: two spaces here.
#                       8 :     do begin
#                       9 :         insert into test(x) values(sqrt(:n));
#                       10 :         n = n - 1;
#                       11 :     end
#                       12 : end
#                   ==================
#               
#                   Confirmed bug on 4.0.0.2195.
#                   Checked 4.0.0.2204: all fine.
#                
# tracker_id:   CORE-6403
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# from __future__ import print_function
#  
#  import os
#  import sys
#  import re
#  import string
#  
#  #import fdb
#  #FB_CLNT=sys.argv[1]
#  #con=fdb.connect(dsn='localhost:e40', fb_library_name = FB_CLNT)
#  #print(con.firebird_version)
#  
#  DEBUG_FLAG=0
#  
#  db_conn.execute_immediate('recreate table test(x int)')
#  db_conn.commit()
#  
#  sttm_list = [
#  '''execute block
#  as
#      declare n integer = 0;
#  begin
#      while/*!*/ (1 / n > 0)
#      do
#      begin
#          n = n - 1;
#      end
#  end'''
#  ,
#  '''execute
#  block as declare n integer = 1; begin
#  while/*!*/
#  (
#     				1 / n > 0
#      			  )
#      do
#      begin
#                n
#          = n - 1;
#      end
#  end'''
#  ,
#  '''execute block
#  as
#  begin
#      while/*!*/ ( (select coalesce(t.x,0) from rdb$database r left join test t on 1=1) <= 1 )
#      do
#      begin
#          insert into test(x) values(1);
#              insert into test(x) values(2);
#                  insert into test(x) values(3);
#      end
#  end'''
#  ,
#  '''execute block
#  as
#      declare n int = 5;
#      declare c int;
#  begin
#      for  /*!*/ select 100/:n from rdb$types into c
#      -- ^^ NB: two spaces here.
#      do begin
#          insert into test(x) values(sqrt(:n));
#          n = n - 1;
#      end
#  end'''
#  ,
#  '''execute block
#  as
#      declare n int = 5;
#      declare c int;
#  begin
#      delete from test;
#      while ( n >= 0 ) do
#      begin
#          for  /*!*/ execute statement (
#              'select 100 / cast(? as int)
#               from rdb$database
#              '
#          ) ( n ) into c
#          -- ^^ NB: two spaces here.
#          do begin
#              -- insert into test(x) values(sqrt(:n));
#              insert into test(x) values( :n );
#          end
#          n = n - 1;
#      end
#  end'''
#  ]
#  
#  sttm_map = {}
#  source_expr_positions_map = {}
#  for i,s in enumerate(sttm_list):
#      sttm_lines = s.splitlines()
#      for j, line in enumerate(sttm_lines):
#          problematic_expr_position = line.find('/*!*/')-5
#          sttm_map[ i, j+1 ] = ( line, 1 + problematic_expr_position )
#          if problematic_expr_position>=0:
#              source_expr_positions_map[ i ] = (j+1, 1 + problematic_expr_position )
#  
#  if DEBUG_FLAG:
#      for k,v in sorted(sttm_map.items()):
#          print(k,':::',v)
#  
#      for k,v in sorted(source_expr_positions_map.items()):
#          print(k,':::',v)
#  
#  
#  # - At block line: 3, col: 1
#  p=re.compile( '(- )?At\\s+block\\s+line(:)?\\s+\\d+(,)?\\s+col(:)?\\s+\\d+', re.IGNORECASE)
#  
#  allchars=string.maketrans('','')
#  nodigits=allchars.translate(allchars, string.digits + string.whitespace)
#  
#  actual_stack_positions_map = {}
#  
#  for i,s in enumerate(sttm_list):
#      if DEBUG_FLAG:
#          print('execute ',i)
#      try:
#          db_conn.execute_immediate(s)
#      except Exception as e:
#          if DEBUG_FLAG:
#              print(e[0])
#          for msg in e[0].splitlines():
#              if DEBUG_FLAG:
#                  print('msg:',msg)
#              if p.match(msg):
#                  if DEBUG_FLAG:
#                      print(p)
#                      print( msg.translate(allchars, nodigits) )
#                  # '- At block line: 3, col: 1' ==>  ' 3  1'
#                  line_col_pair = msg.translate(allchars, nodigits).split()
#                  actual_stack_positions_map[ i ] = ( int(line_col_pair[0]), int(line_col_pair[1]), e[0] )
#                  
#  if DEBUG_FLAG:
#      for k,v in sorted(actual_stack_positions_map.items()):
#          print(k,'###',v)
#  
#  for k,v in sorted(source_expr_positions_map.items()):
#      w = actual_stack_positions_map.get(k)
#      if w and v[:2] == w[:2]:
#          print('Test %d PASSED' % k) # expected line/col in source code matches error stack pair.
#      else:
#          print(k, 'UNEXPECTED MISMATCH between expected and actual values of line/col:')
#          print('  * expected (position of problematic token): %d, %d' % (v[0], v[1]) )
#          if w:
#              print('  * actual (result of error message parsing): %d, %d' % (w[0], w[1]) )
#              print('  * source message of error:')
#              for i in w[2].splitlines():
#                  print( ' ' * 8, i )
#          else:
#              print('  * actual: NONE')
#  
#          print('Expression:')
#          for i,s in enumerate( sttm_list[k].splitlines() ):
#              if i == 0:
#                  print( '%s %s' % (" " * 6, ''.join( [ '....:....' + str(j) for j in range(1,9)] ) ) )
#                  print( '%s : %s' % ( " " * 4, "1234567890" * 8) )
#              print( '%s : %s' % ( "{:4g}".format(i+1), s) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Test 0 PASSED
    Test 1 PASSED
    Test 2 PASSED
    Test 3 PASSED
    Test 4 PASSED
  """

@pytest.mark.version('>=4.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


