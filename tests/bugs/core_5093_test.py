#coding:utf-8
#
# id:           bugs.core_5093
# title:        ISQL extract command lose COMPUTED BY field types
# decription:   
#                  Test creates table with fields of (almost) all possible datatypes.
#                  Then we apply "ALTER TABLE ALTER FIELD ..., ALTER FIELD ..." so that every field is changed,
#                  either by updating its computed-by value or type (for text fields - also add/remove charset).
#                  Expression for ALTER TABLE - see literal "alter_table_ddl", encoded in UTF8.
#                  NB: changing character set should NOT be reflected on SQLDA output (at least for current FB builds).
#                  Confirmed bug on  WI-V3.0.0.32134 (RC1), fixed on: WI-V3.0.0.32311.
#                  :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#                  ::: NB ::: 
#                  It is possible that this test need to be adjusted soon for FB 3.0, because current SQLDA
#                  output is not affected by changing of field character set (adding or removing or updating).
#                  Sent letter to Adriano, 02-feb-2015 15:25, waiting for reply.
#                
# tracker_id:   CORE-5093
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('DATABASE: LOCALHOST.*BUGS.CORE_5093.FDB.*', ''), ('.*TABLE: T1.*', ''), ('.*MESSAGE FIELD COUNT.*', '')]

init_script_1 = """
    recreate table t1 (
         n0 int

        ,si smallint computed by(32767)
        ,bi bigint computed by (2147483647)
        ,s2 smallint computed by ( mod(bi, nullif(si,0)) )

        ,dx double precision computed by (pi())
        ,fx float computed by (dx*dx)
        ,nf numeric(3,1) computed by (fx)

        ,dt date computed by ('now')
        ,tm time computed by ('now')
        
        ,c_change_cb_value char character set win1251 computed by ('ы') -- for this field we only will change value inside its COMPUTED_BY clause; this should NOT bring any affect on SQLDA output.
        ,c_change_charset char character set win1252 computed by ('å') -- for this field we'll only change CHARACTER SET, but this will not has effect (at least on current FB builds)
        ,c_change_length char character set utf8 computed by ('∑') -- for this field we'll only increase its length
       
        ,b_change_cb_value blob character set win1251 computed by ('ы') -- for this field we only will change value inside its COMPUTED_BY clause; this should NOT bring any affect on SQLDA output.
        ,b_change_charset blob character set win1252 computed by ('å') -- for this field we'll only change CHARACTER SET, but this will not has effect (at least on current FB builds)
        ,b_remove_charset blob character set win1252 computed by ('ä') -- for this field we'll only REMOVE its CHARACTER SET; this should change this blob subtype from 1 to 0
        ,b_added_charset blob computed by ('∑') -- for this field we'll only ADD definition of CHARACTER SET; this should change this blob subtype from 0 to 1
    ); 
    commit;  
  """

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  
#  db_conn.close()
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_file="$(DATABASE_LOCATION)bugs.core_5093.fdb"
#  
#  f_sqlda_init = open( os.path.join(context['temp_directory'],'tmp_sqlda_5093_init.log') , 'w')
#  f_sqlda_init.close()
#  
#  runProgram( 'isql',[dsn, '-q', '-m', '-o', f_sqlda_init.name], 'set sqlda_display on; select * from t1;')
#  
#  alter_table_ddl=u'''
#      alter table t1
#          alter si type int computed by (32767) -- LONG
#         ,alter bi type int computed by (2147483647) -- LONG
#         ,alter s2 type smallint computed by ( 1 + mod(bi, nullif(si,0)) ) -- SHORT
#  
#         ,alter dx type float computed by( pi()/2 ) -- FLOAT
#         ,alter fx type float computed by (dx*dx*dx) -- FLOAT
#         ,alter nf type bigint computed by (fx * fx) -- INT64
#         
#         ,alter dt type date computed by ('today') -- DATE
#         ,alter tm type timestamp computed by ('now') -- TIMESTAMP
#         
#         ,alter c_change_cb_value type char character set win1251 computed by ('Ё') -- TEXT
#         ,alter c_change_charset type char character set utf8 computed by ('Æ') -- TEXT
#         ,alter c_change_length type char(2) computed by ('∑∞')    -- TEXT
#         
#          -- All these fields, of course, should remain in type = BLOB, 
#          -- but when charset is removed (field "b_remove_charset") then blob subtype has to be changed to 0,
#          -- and when we ADD charset (field "b_added_charset") then blob subtype has to be changed to 1.
#         ,alter b_change_cb_value type blob character set win1251 computed by ('Ё') -- BLOB
#         ,alter b_change_charset type blob character set iso8859_1 computed by ('å') -- BLOB
#         ,alter b_remove_charset type blob /*character set win1252 */ computed by ('Æ') -- BLOB
#         ,alter b_added_charset type blob character set utf8 computed by ('∞')    -- BLOB
#      ;
#      commit;
#      set sqlda_display on; 
#      select * from t1;
#      exit;
#  '''
#  
#  f_sqlda_last = open( os.path.join(context['temp_directory'],'tmp_sqlda_5093_last.log') , 'w')
#  f_sqlda_last.close()
#  
#  runProgram( 'isql',[dsn, '-q', '-m', '-o', f_sqlda_last.name], alter_table_ddl)
#  
#  with open( f_sqlda_init.name,'r') as f:
#      for line in f:
#              print( ' '.join(line.split()).upper() )
#  
#  with open( f_sqlda_last.name,'r') as f:
#      for line in f:
#              print( ' '.join(line.split()).upper() )
#  f.close()
#  
#  ###############################
#  # Cleanup.
#  
#  f_list=[]
#  f_list.append(f_sqlda_init)
#  f_list.append(f_sqlda_last)
#  
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i].name):
#          os.remove(f_list[i].name)
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
        01: SQLTYPE: 496 LONG NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
        : NAME: N0 ALIAS: N0
        02: SQLTYPE: 500 SHORT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 2
        : NAME: SI ALIAS: SI
        03: SQLTYPE: 580 INT64 NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 8
        : NAME: BI ALIAS: BI
        04: SQLTYPE: 500 SHORT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 2
        : NAME: S2 ALIAS: S2
        05: SQLTYPE: 480 DOUBLE NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 8
        : NAME: DX ALIAS: DX
        06: SQLTYPE: 482 FLOAT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
        : NAME: FX ALIAS: FX
        07: SQLTYPE: 500 SHORT NULLABLE SCALE: -1 SUBTYPE: 1 LEN: 2
        : NAME: NF ALIAS: NF
        08: SQLTYPE: 570 SQL DATE NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
        : NAME: DT ALIAS: DT
        09: SQLTYPE: 560 TIME NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
        : NAME: TM ALIAS: TM
        10: SQLTYPE: 452 TEXT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4 CHARSET: 4 UTF8
        : NAME: C_CHANGE_CB_VALUE ALIAS: C_CHANGE_CB_VALUE
        11: SQLTYPE: 452 TEXT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4 CHARSET: 4 UTF8
        : NAME: C_CHANGE_CHARSET ALIAS: C_CHANGE_CHARSET
        12: SQLTYPE: 452 TEXT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4 CHARSET: 4 UTF8
        : NAME: C_CHANGE_LENGTH ALIAS: C_CHANGE_LENGTH
        13: SQLTYPE: 520 BLOB NULLABLE SCALE: 0 SUBTYPE: 1 LEN: 8 CHARSET: 4 UTF8
        : NAME: B_CHANGE_CB_VALUE ALIAS: B_CHANGE_CB_VALUE
        14: SQLTYPE: 520 BLOB NULLABLE SCALE: 0 SUBTYPE: 1 LEN: 8 CHARSET: 4 UTF8
        : NAME: B_CHANGE_CHARSET ALIAS: B_CHANGE_CHARSET
        15: SQLTYPE: 520 BLOB NULLABLE SCALE: 0 SUBTYPE: 1 LEN: 8 CHARSET: 4 UTF8
        : NAME: B_REMOVE_CHARSET ALIAS: B_REMOVE_CHARSET
        16: SQLTYPE: 520 BLOB NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 8
        : NAME: B_ADDED_CHARSET ALIAS: B_ADDED_CHARSET  
  
  
    01: SQLTYPE: 496 LONG NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
    : NAME: N0 ALIAS: N0
    02: SQLTYPE: 496 LONG NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
    : NAME: SI ALIAS: SI
    03: SQLTYPE: 496 LONG NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
    : NAME: BI ALIAS: BI
    04: SQLTYPE: 500 SHORT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 2
    : NAME: S2 ALIAS: S2
    05: SQLTYPE: 482 FLOAT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
    : NAME: DX ALIAS: DX
    06: SQLTYPE: 482 FLOAT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
    : NAME: FX ALIAS: FX
    07: SQLTYPE: 580 INT64 NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 8
    : NAME: NF ALIAS: NF
    08: SQLTYPE: 570 SQL DATE NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4
    : NAME: DT ALIAS: DT
    09: SQLTYPE: 510 TIMESTAMP NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 8
    : NAME: TM ALIAS: TM
    10: SQLTYPE: 452 TEXT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4 CHARSET: 4 UTF8
    : NAME: C_CHANGE_CB_VALUE ALIAS: C_CHANGE_CB_VALUE
    11: SQLTYPE: 452 TEXT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 4 CHARSET: 4 UTF8
    : NAME: C_CHANGE_CHARSET ALIAS: C_CHANGE_CHARSET
    12: SQLTYPE: 452 TEXT NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 8 CHARSET: 4 UTF8
    : NAME: C_CHANGE_LENGTH ALIAS: C_CHANGE_LENGTH
    13: SQLTYPE: 520 BLOB NULLABLE SCALE: 0 SUBTYPE: 1 LEN: 8 CHARSET: 4 UTF8
    : NAME: B_CHANGE_CB_VALUE ALIAS: B_CHANGE_CB_VALUE
    14: SQLTYPE: 520 BLOB NULLABLE SCALE: 0 SUBTYPE: 1 LEN: 8 CHARSET: 4 UTF8
    : NAME: B_CHANGE_CHARSET ALIAS: B_CHANGE_CHARSET
    15: SQLTYPE: 520 BLOB NULLABLE SCALE: 0 SUBTYPE: 0 LEN: 8
    : NAME: B_REMOVE_CHARSET ALIAS: B_REMOVE_CHARSET
    16: SQLTYPE: 520 BLOB NULLABLE SCALE: 0 SUBTYPE: 1 LEN: 8 CHARSET: 0 NONE
    : NAME: B_ADDED_CHARSET ALIAS: B_ADDED_CHARSET
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


