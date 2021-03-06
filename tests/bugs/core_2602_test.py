#coding:utf-8
#
# id:           bugs.core_2602
# title:        Attachments using NONE charset may cause reads from MON$ tables to fail
# decription:   
#               	Fully refactored 05-feb-2018. Apply HASH() functions to unicode mon$sql_text in order to returnonly numeric value
#               	rather than non-translatable unicode representation which can differ on machines with different codepage / OS.
#               	For example, instead of (on Win XP with codepage 1251):
#               	   r2none (u'othr', u "select '123\\ u0413\\ u040e\\ u0413\\ xa9456' from mon$database", 4, u'UTF8')
#               	- result was different on Win 2008 R2 with codepage 437
#               	   r2none (u'othr', u "select '123\\ xc3\\ xa1\\ xc3\\ xa9456' from mon$database", 4, u'UTF8')
#               	---------------------------------------------------------------------------------------
#               	Confirmed bug on 2.1.3.18185, got exception:
#               	   fdb.fbcore.DatabaseError: ('Cursor.fetchone:
#               - SQLCODE: -901
#               - lock conflict on no wait transaction', -901, 335544345)
#               	- just after issued 1st cursor result.
#               	No error since 2.5.0.26074.
#               	
#               	25.12.2019: added filtering expr to WHERE clause in order to prevent from passing through records related to RDB$AUTH table (4.x).
#               	Last tested 25.12.2019 on:
#               		4.0.0.1707 SS: 1.448s.
#               		4.0.0.1346 SC: 1.295s.
#               		4.0.0.1691 CS: 2.009s.
#               		3.0.5.33218 SS: 0.733s.
#               		3.0.5.33084 SC: 0.673s.
#               		3.0.5.33212 CS: 1.755s.
#               		2.5.9.27149 SC: 0.218s.
#               		2.5.9.27119 SS: 2.411s.
#                
# tracker_id:   CORE-2602
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import fdb
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  db_conn.close()
#  
#  c1none=fdb.connect(dsn=dsn,charset='none')
#  c1utf8=fdb.connect(dsn=dsn,charset='utf8')
#  
#  c2none=fdb.connect(dsn=dsn,charset='none')
#  c2utf8=fdb.connect(dsn=dsn,charset='utf8')
#  
#  r1none = c1none.cursor()
#  r1utf8 = c1utf8.cursor()
#  
#  r2none = c2none.cursor()
#  r2utf8 = c2utf8.cursor()
#  
#  # In attachment with charset = NONE we start query to mon$database which includes two non-ascii characters:
#  # 1) Unicode Character 'LATIN SMALL LETTER A WITH ACUTE' (U+00E1)   
#  # 2) Unicode Character 'LATIN SMALL LETTER E WITH ACUTE' (U+00E9)
#  r1none.execute("select '123áé456' from mon$database")
#  
#  sql='''
#      select 
#           iif(s.mon$attachment_id = current_connection, 'this', 'othr') as attach 
#           -- do NOT return SQL text of query with non-ascii characters: it can be displayed differently
#           -- depending on machine codepage (or OS?):
#           -- >>> disabled 05-feb-2018 >>> , iif(s.mon$sql_text like '%123%456%', s.mon$sql_text, '') as sql_text
#           -- Use HASH(sql_text) instead. Bug (in 2.1.3) still can be reproduces with hash() also:
#          ,hash(s.mon$sql_text) as sql_text_hash
#          ,trim(c.rdb$character_set_name) as charset_name
#      from mon$statements s
#      join mon$attachments a on s.mon$attachment_id = a.mon$attachment_id
#      join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
#      where
#          s.mon$attachment_id != current_connection 
#          and s.mon$sql_text NOT containing 'mon$statements'
#          and s.mon$sql_text NOT containing 'rdb$auth'
#          and a.mon$remote_protocol is not null
#  '''
#  
#  r2none.execute(sql)
#  for r in r2none:
#    #print( ' '.join( 'THIS connect with charset NONE. OTHER connect tiwh charset UTF8.', 'WE see other sqltest hash as: ', r[0], '; sql_text_hash: ', str( r[1] ), '; charset_name', r[2] ) )
#    #print('r2none',r)
#    print( ' '.join( ( 'Attach: r2none.', r[0], '; sql_text_hash: ', str( r[1] ), '; charset_name', r[2] ) ) )
#  
#  r2utf8.execute(sql)
#  for r in r2utf8:
#    print( ' '.join( ( 'Attach: r2utf8.', r[0], '; sql_text_hash: ', str( r[1] ), '; charset_name', r[2] ) ) )
#    #print('r2utf8',r)
#  
#  c1none.close()
#  #----------------------------
#  
#  r1utf8.execute("select '123áé456' from mon$database")
#  
#  c2none.commit()
#  c2utf8.commit()
#  
#  r2none.execute(sql)
#  for r in r2none:
#    #print('r2none', r)
#    print( ' '.join( ( 'Attach: r2none.', r[0], '; sql_text_hash: ', str( r[1] ), '; charset_name', r[2] ) ) )
#  
#  r2utf8.execute(sql)
#  for r in r2utf8:
#    #print('r2utf8', r)
#    print( ' '.join( ( 'Attach: r2utf8.', r[0], '; sql_text_hash: ', str( r[1] ), '; charset_name', r[2] ) ) )
#  
#  c1utf8.close()
#  #---------------------------
#  
#  c2none.close()
#  c2utf8.close()
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Attach: r2none. othr ; sql_text_hash:  98490476833044645 ; charset_name NONE
    Attach: r2utf8. othr ; sql_text_hash:  98490476833044645 ; charset_name NONE
    Attach: r2none. othr ; sql_text_hash:  97434734411675813 ; charset_name UTF8
    Attach: r2utf8. othr ; sql_text_hash:  97434734411675813 ; charset_name UTF8
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


