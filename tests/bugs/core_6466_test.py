#coding:utf-8
#
# id:           bugs.core_6466
# title:        Comments before the first line of code are removed (when extract metadata)
# decription:   
#                  Lot of comments (multi-line blocks) are inserted before each clause/token of created SP
#                  (in its declaration of name, input and output parameters, sections of variables and after
#                  final 'end').
#                  Comments before 'AS' clause will be removed after SP commit (i.e. they must not be shown
#                  when metadata is axtracted - at least for current versions of FB).
#                  First comment _after_ 'AS' clause (and before 1st 'declare variable' statement) *must*
#                  be preserved.
#                  Comment after final 'end' of procedure must also be preserved.
#               
#                  Confirmed bug on:
#                      * 4.0.0.2353 - final comment ('950' in this script) was not stored;
#                      * 3.0.8.33401 - comments before first declaration of variable ('900') and after final
#                                      'end' ('950') were not stored.
#                  Checked on 4.0.0.2365, 3.0.8.33415 -- all fine.
#                
# tracker_id:   CORE-6466
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = [('^((?!comment-[\\d]+).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """
    set term ^;
    create or alter procedure sp_test1
    		/*
    		comment-100
    		*/
    	( 
    		/*
    		comment-150
    		*/
    	int_a int
    		/*
    		comment-200
    		*/
    	 ,
    		/*
    		comment-230
    		*/
    	 int_b int
    		/*
    		comment-250
    		*/
    	)
    		/*
    		comment-300
    		*/
    returns 
    		/*
    		comment-400
    		*/
    	( 
    		/*
    		comment-500
    		*/
          out_a
    		/*
    		comment-600
    		*/
    	  int
    		/*
    		comment-700
    		*/
    	 ,out_b int
    		/*
    		comment-750
    		*/
    	)
    		/*
    		comment-800
    		*/
    as
    		/*
    		comment-900
    		*/
    	declare
    		/*
    		comment-910
    		*/
    	int_c
    		/*
    		comment-920
    		*/
    	int  = 2
    		/*
    		comment-930
    		*/
    	;
    		/*
    		comment-940
    		*/
    begin
    	/* code */
    	int_b=int_a+int_c+2;
    	suspend;
    end
    		/*
    		comment-950
    		*/
    ^
    commit
    ^
    set term ;^ 
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  runProgram('isql', [dsn, '-x', '-user', user_name, '-pas', user_password], )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    comment-900
    comment-910
    comment-920
    comment-930
    comment-940
    comment-950
  """

@pytest.mark.version('>=3.0.8')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


