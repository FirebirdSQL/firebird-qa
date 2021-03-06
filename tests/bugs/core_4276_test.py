#coding:utf-8
#
# id:           bugs.core_4276
# title:        Error on create table with "CHARACTER SET DOS775" field
# decription:   
#                   Confirmed problem on 2.5.3.26780:
#                       Statement failed, SQLSTATE = 2C000
#                       bad parameters on attach or create database
#                       -CHARACTER SET DOS775 is not defined
#                   Checked on 3.0.0.32136 RC1  - all OK.
#               
#                   02-mar-2021. Re-implemented in order to have ability to run this test on Linux.
#                   Test encodes to UTF8 all needed statements (SET NAMES; CONNECT; DDL and DML) and stores this text in .sql file.
#                   NOTE: 'SET NAMES' contain character set that must be used for reproducing problem (DOS775 in this test).
#                   Then ISQL is launched in separate (child) process which performs all necessary actions (using required charset).
#                   Result will be redirected to log(s) which will be opened further via codecs.open(...encoding='cp775').
#                   Finally, its content will be converted to UTF8 for showing in expected_stdout.
#               
#                   Checked on:
#                           * Windows: 4.0.0.2377, 3.0.8.33420, 2.5.9.27152
#                           * Linux:   4.0.0.2377, 3.0.8.33415
#               
#                 
# tracker_id:   CORE-4276
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.5
# resources: None

substitutions_1 = [('BLOB_CONTENT.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  
#  import os
#  import codecs
#  import subprocess
#  import time
#  
#  db_conn.close()
#  
#  #--------------------------------------------
#  
#  def flush_and_close( file_handle ):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#  
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb') and file_handle.name != os.devnull:
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if type(f_names_list[i]) == file:
#            del_name = f_names_list[i].name
#         elif type(f_names_list[i]) == str:
#            del_name = f_names_list[i]
#         else:
#            print('Unrecognized type of element:', f_names_list[i], ' - can not be treated as file.')
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  # Code to be executed further in separate ISQL process:
#  #############################
#  sql_txt='''
#      set bail on;
#      set names dos775;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#  
#  	recreate table "ĄČĘĢÆĖŠŚÖÜØ£"(
#  		"ąčęėįšųūž" varchar(50) character set dos775
#  		,"Õisu ja kariste järved" blob sub_type 1 character set dos775
#  	);
#  	commit;
#  	show table;
#  	show table "ĄČĘĢÆĖŠŚÖÜØ£";
#  	insert into "ĄČĘĢÆĖŠŚÖÜØ£"("ąčęėįšųūž", "Õisu ja kariste järved") 
#  	values(
#  		'ÓßŌŃõÕµńĶķĻļņĒŅ',
#  		'Green - viens no trim primārās krāsas, zaļā tiek uzskatīts diapazontsvetov spektrs ar viļņa 
#  		garumu aptuveni 500-565 nanometri. Sistēma CMYK druka zaļā iegūst, sajaucot dzelteno un 
#  		zilganzaļi (cyan).Dabā, Catalpa - zaļa augs.
#  		Krāsu zaļie augi ir dabiski, ka cilvēks etalonomzeleni.
#  		Zaļā koku varde.
#  		Ir plaši izplatīti dabā. Lielākā daļa augu ir zaļā krāsā, jo tie satur pigmentu fotosintēzes - 
#  		hlorofilu (hlorofils absorbē lielu daļu no sarkano stariem saules spektra, atstājot uztveri 
#  		atstarotās un filtrē zaļā krāsā). Dzīvnieki ar zaļo krāsu tā izmantošanu maskēties fona augiem.'
#  	);
#  	set list on;
#  	set blob all;
#  	select "ąčęėįšųūž", "Õisu ja kariste järved" as blob_content
#  	from "ĄČĘĢÆĖŠŚÖÜØ£";
#  
#  ''' % dict(globals(), **locals())
#  
#  f_run_sql = open( os.path.join(context['temp_directory'], 'tmp_4276_dos775.sql'), 'w' )
#  f_run_sql.write( sql_txt.decode('utf8').encode('cp775') )
#  flush_and_close( f_run_sql )
#  
#  # result: file tmp_4276_dos775.sql is encoded in dos775
#  
#  f_run_log = open( os.path.splitext(f_run_sql.name)[0]+'.log', 'w')
#  subprocess.call( [ context['isql_path'], '-q', '-i', f_run_sql.name ],
#                   stdout = f_run_log,
#                   stderr = subprocess.STDOUT
#                 )
#  flush_and_close( f_run_log ) # result: output will be encoded in dos775
#  
#  with codecs.open(f_run_log.name, 'r', encoding='cp775' ) as f:
#      result_in_dos775 = f.readlines()
#  
#  for i in result_in_dos775:
#      print( i.encode('utf8') )
#  
#  # cleanup:
#  ###########
#  cleanup( (f_run_sql, f_run_log) )
#    
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
					   ĄČĘĢÆĖŠŚÖÜØ£        
	ąčęėįšųūž                       VARCHAR(50) CHARACTER SET DOS775 Nullable 
	Õisu ja kariste järved          BLOB segment 80, subtype TEXT CHARACTER SET DOS775 Nullable 

	ąčęėįšųūž                       ÓßŌŃõÕµńĶķĻļņĒŅ
	BLOB_CONTENT                    80:0
	Green - viens no trim primārās krāsas, zaļā tiek uzskatīts diapazontsvetov spektrs ar viļņa 
	garumu aptuveni 500-565 nanometri. Sistēma CMYK druka zaļā iegūst, sajaucot dzelteno un 
	zilganzaļi (cyan).Dabā, Catalpa - zaļa augs.
	Krāsu zaļie augi ir dabiski, ka cilvēks etalonomzeleni.
	Zaļā koku varde.
	Ir plaši izplatīti dabā. Lielākā daļa augu ir zaļā krāsā, jo tie satur pigmentu fotosintēzes - 
	hlorofilu (hlorofils absorbē lielu daļu no sarkano stariem saules spektra, atstājot uztveri 
	atstarotās un filtrē zaļā krāsā). Dzīvnieki ar zaļo krāsu tā izmantošanu maskēties fona augiem.  
  """

@pytest.mark.version('>=2.5.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


