#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_cast_isql
# title:        GTCS/tests/PROC_CAST1_ISQL.script ... PROC_CAST10_ISQL.script
# decription:   
#               	Original tests see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_CAST1_ISQL.script
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_CAST2_ISQL.script
#                       ...
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_CAST10_ISQL.script
#               
#                   Checked on WI-V3.0.6.33283; WI-T4.0.0.1881.
#                
# tracker_id:   
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = [('BLOB_ID.*', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import time
#  import subprocess
#  from fdb import services
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
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
#      for f in f_names_list:
#         if type(f) == file:
#            del_name = f.name
#         elif type(f) == str:
#            del_name = f
#         else:
#            print('Unrecognized type of element:', f, ' - can not be treated as file.')
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#      
#  #--------------------------------------------
#  
#  sql_gen_ddl = os.path.join(context['files_location'],'gtcs-cast-gen-ddl.sql')
#  
#  f_init_run=open( os.path.join(context['temp_directory'],'tmp_gtcs_cast_ddl.sql'), 'w', buffering = 0)
#  f_init_err=open( os.path.join(context['temp_directory'],'tmp_gtcs_cast_ddl.err'), 'w', buffering = 0)
#  subprocess.call( [context['isql_path'], dsn, '-q', '-i', sql_gen_ddl], stdout=f_init_run, stderr=f_init_err )
#  flush_and_close( f_init_run )
#  flush_and_close( f_init_err )
#  
#  
#  f_cast_log=open( os.path.join(context['temp_directory'],'tmp_gtcs_cast_run.log'), 'w', buffering = 0)
#  f_cast_err=open( os.path.join(context['temp_directory'],'tmp_gtcs_cast_run.err'), 'w', buffering = 0)
#  subprocess.call( [context['isql_path'], dsn, '-q', '-i', f_init_run.name], stdout=f_cast_log, stderr=f_cast_err )
#  flush_and_close( f_cast_log )
#  flush_and_close( f_cast_err )
#  
#  # CHECKS:
#  #########
#  for g in (f_init_err, f_cast_err):
#      with open(g.name, 'r') as f:
#          for line in f:
#              if line.split():
#                  print('UNEXPECTED OUTPUT in ' + os.path.split(g.name)[-1] + ': ' + line )
#  
#  with open(f_cast_log.name, 'r') as f:
#      for line in f:
#          if line.split():
#              print( line.strip() )
#  
#  # CLEANUP:
#  ##########
#  # do NOT remove this pause otherwise some of logs will not be enable for deletion and test will finish with 
#  # Exception raised while executing Python test script. exception: WindowsError: 32
#  time.sleep(1)
#  cleanup( ( f_init_run, f_init_err, f_cast_log, f_cast_err ) )
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    bigint_bigint                   80 
    BLOB_ID                         0:1 
    80.4450 
    bigint_char(10)                 80.4450 
    bigint_date                     2003-04-22 
    bigint_decimal( 4,2)            0.04 
    bigint_decimal( 4,2)            0.05 
    bigint_decimal(10,4)            80.4450 
    bigint_double precision         80.44499999999999 
    bigint_float                    80.445 
    bigint_nchar(10)                80.4450 
    bigint_numeric( 4,2)            0.04 
    bigint_numeric( 4,2)            0.05 
    bigint_numeric(10,4)            80.4450 
    bigint_smallint                 80 
    bigint_time                     01:02:03.0000 
    bigint_timestamp                2003-04-22 11:35:39.0000 
    bigint_varchar(10)              80.4450 
    blob_bigint                     9223372036854775807 
    blob_boolean                    <true> 
    blob_char(30)                   81985529216487135 
    blob_date                       2004-02-29 
    blob_decimal(5,2)               80.45 
    blob_double precision           80.44499999999999 
    blob_float                      80.445 
    blob_int                        -2147483648 
    blob_nchar(30)                  81985529216487135 
    blob_numeric(5,2)               80.45 
    blob_smallint                   32767 
    blob_time                       01:02:03.4560 
    blob_varchar(30)                81985529216487135 
    char(30)_bigint                 9223372036854775807 
    BLOB_ID                         0:1 
    81985529216487135 
    char(30)_boolean                <true> 
    char(30)_date                   2004-02-29 
    char(30)_decimal(5,2)           80.45 
    char(30)_double precision       80.44499999999999 
    char(30)_float                  80.445 
    char(30)_int                    -2147483648 
    char(30)_nchar(30)              81985529216487135 
    char(30)_numeric(5,2)           80.45 
    char(30)_smallint               32767 
    char(30)_time                   01:02:03.4560 
    char(30)_varchar(30)            81985529216487135 
    date_bigint                     147558 
    BLOB_ID                         0:1 
    2004-02-29 
    date_char(10)                   2004-02-29 
    date_decimal(4,2)               2.00 
    date_double precision           2.000000000000000 
    date_float                      2 
    date_int                        147558 
    date_nchar(10)                  2004-02-29 
    date_numeric(4,2)               2.00 
    date_smallint                   1461 
    date_time                       01:02:05.0000 
    date_timestamp                  2003-02-03 01:02:03.0000 
    date_varchar(10)                2004-02-29 
    decimal(4,2)_bigint             80 
    BLOB_ID                         0:1 
    0.05 
    BLOB_ID                         0:3 
    0.06 
    BLOB_ID                         0:5 
    0.08 
    decimal(4,2)_char(10)           0.05 
    decimal(4,2)_char(10)           0.06 
    decimal(4,2)_char(10)           0.08 
    decimal(4,2)_date               2003-04-22 
    decimal(4,2)_decimal(4,2)       0.05 
    decimal(4,2)_decimal(4,2)       0.06 
    decimal(4,2)_decimal(4,2)       0.08 
    decimal(4,2)_double precision   80.45000000000000 
    decimal(4,2)_double precision   0.05000000000000000 
    decimal(4,2)_double precision   0.06000000000000000 
    decimal(4,2)_double precision   0.08000000000000000 
    decimal(4,2)_float              80.449997 
    decimal(4,2)_float              0.050000001 
    decimal(4,2)_float              0.059999999 
    decimal(4,2)_float              0.079999998 
    decimal(4,2)_int                80 
    decimal(4,2)_nchar(10)          0.05 
    decimal(4,2)_nchar(10)          0.06 
    decimal(4,2)_nchar(10)          0.08 
    decimal(4,2)_numeric(4,2)       0.05 
    decimal(4,2)_numeric(4,2)       0.06 
    decimal(4,2)_numeric(4,2)       0.08 
    decimal(4,2)_smallint           80 
    decimal(4,2)_time               01:03:23.4500 
    decimal(4,2)_timestamp          2003-04-22 11:50:03.0000 
    decimal(4,2)_varchar(10)        0.05 
    decimal(4,2)_varchar(10)        0.06 
    decimal(4,2)_varchar(10)        0.08 
    double precision_bigint         80 
    BLOB_ID                         0:1 
    80.44499999999999 
    double precision_char(10)       80.445000 
    double precision_date           2003-04-22 
    ouble precision_decimal(10,4)   80.4450 
    double precision_decimal(4,2)   0.05 
    double precision_decimal(4,2)   0.06 
    double precision_decimal(4,2)   0.08 
    double precision_float          80.445 
    double precision_int            80 
    double precision_nchar(10)      80.445000 
    ouble precision_numeric(10,4)   80.4450 
    double precision_numeric(4,2)   0.05 
    double precision_numeric(4,2)   0.06 
    double precision_numeric(4,2)   0.08 
    double precision_smallint       80 
    double precision_time           01:03:23.4450 
    double precision_timestamp      2003-04-22 11:42:51.0000 
    double precision_varchar(10)    80.445000 
    float_bigint                    80 
    BLOB_ID                         0:1 
    80.445000 
    float_char(10)                  80.445000 
    float_date                      2003-04-22 
    float_decimal(10,4)             80.4450 
    float_decimal(4,2)              0.05 
    float_double precision          80.44499969482422 
    float_int                       80 
    float_nchar(10)                 80.445000 
    float_numeric( 4,2)             0.05 
    float_numeric(10,4)             80.4450 
    float_smallint                  80 
    float_time                      01:03:23.4450 
    float_timestamp                 2003-04-22 11:42:50.9736 
    float_varchar(10)               80.445000 
    int_bigint                      80 
    BLOB_ID                         0:1 
    80.4450 
    int_char(10)                    80.4450 
    int_date                        2003-04-22 
    int_decimal( 4,2)               0.04 
    int_decimal( 4,2)               0.05 
    int_decimal(10,4)               80.4450 
    int_double precision            80.44499999999999 
    int_float                       80.445 
    int_nchar(10)                   80.4450 
    int_numeric( 4,2)               0.04 
    int_numeric( 4,2)               0.05 
    int_numeric(10,4)               80.4450 
    int_smallint                    80 
    int_time                        01:02:03.0000 
    int_timestamp                   2003-04-22 11:35:39.0000 
    int_varchar(10)                 80.4450 
    nchar(30)_bigint                9223372036854775807 
    BLOB_ID                         0:1 
    81985529216487135 
    nchar(30)_boolean               <true> 
    nchar(30)_char(30)              81985529216487135 
    nchar(30)_date                  2004-02-29 
    nchar(30)_decimal(5,2)          80.45 
    nchar(30)_double precision      80.44499999999999 
    nchar(30)_float                 80.445 
    nchar(30)_int                   -2147483648 
    nchar(30)_numeric(5,2)          80.45 
    nchar(30)_smallint              32767 
    nchar(30)_time                  01:02:03.4560 
    nchar(30)_varchar(30)           81985529216487135 
    numeric(4,2)_bigint             80 
    BLOB_ID                         0:1 
    0.05 
    BLOB_ID                         0:3 
    0.06 
    BLOB_ID                         0:5 
    0.08 
    numeric(4,2)_char(10)           0.05 
    numeric(4,2)_char(10)           0.06 
    numeric(4,2)_char(10)           0.08 
    numeric(4,2)_date               2003-04-22 
    numeric(4,2)_decimal(4,2)       0.05 
    numeric(4,2)_decimal(4,2)       0.06 
    numeric(4,2)_decimal(4,2)       0.08 
    numeric(4,2)_double precision   80.45000000000000 
    numeric(4,2)_double precision   0.05000000000000000 
    numeric(4,2)_double precision   0.06000000000000000 
    numeric(4,2)_double precision   0.08000000000000000 
    numeric(4,2)_float              80.449997 
    numeric(4,2)_float              0.050000001 
    numeric(4,2)_float              0.059999999 
    numeric(4,2)_float              0.079999998 
    numeric(4,2)_int                80 
    numeric(4,2)_nchar(10)          0.05 
    numeric(4,2)_nchar(10)          0.06 
    numeric(4,2)_nchar(10)          0.08 
    numeric(4,2)_numeric(4,2)       0.05 
    numeric(4,2)_numeric(4,2)       0.06 
    numeric(4,2)_numeric(4,2)       0.08 
    numeric(4,2)_smallint           80 
    numeric(4,2)_time               01:03:23.4500 
    numeric(4,2)_timestamp          2003-04-22 11:50:03.0000 
    numeric(4,2)_varchar(10)        0.05 
    numeric(4,2)_varchar(10)        0.06 
    numeric(4,2)_varchar(10)        0.08 
    smallint_bigint                 10922 
    BLOB_ID                         0:1 
    80.4450 
    smallint_char(10)               80.4450 
    smallint_date                   2003-11-19 
    smallint_decimal( 4,2)          80.45 
    smallint_decimal(10,4)          80.4450 
    smallint_double precision       80.44499999999999 
    smallint_float                  80.445 
    smallint_int                    -10922 
    smallint_int                    10922 
    smallint_nchar(10)              80.4450 
    smallint_numeric( 4,2)          80.45 
    smallint_numeric(10,4)          80.4450 
    smallint_time                   01:06:55.0000 
    smallint_timestamp              2003-11-21 01:02:03.0000 
    smallint_varchar(10)            80.4450 
    time_bigint                     82677 
    BLOB_ID                         0:1 
    01:02:03.0000 
    time_char(13)                   01:02:03.0000 
    time_date                       2003-02-01 
    time_decimal(10,2)              82676.67 
    time_double precision           82676.66600000000 
    time_float                      82676.664 
    time_int                        82677 
    time_nchar(13)                  01:02:03.0000 
    time_numeric(10,2)              82676.67 
    time_smallint                   3661 
    time_timestamp                  2003-02-01 01:02:03.0000 
    time_varchar(13)                01:02:03.0000 
    timestamp_bigint                1 
    BLOB_ID                         0:1 
    2004-02-29 01:02:03.4560 
    timestamp_char(30)              2004-02-29 01:02:03.4560 
    timestamp_date                  2004-02-29 
    timestamp_decimal(10,2)         0.58 
    timestamp_double precision      0.5755401160000000 
    timestamp_float                 0.57554013 
    timestamp_int                   1 
    timestamp_nchar(30)             2004-02-29 01:02:03.4560 
    timestamp_numeric(10,2)         0.58 
    timestamp_smallint              0 
    timestamp_time                  01:02:03.0000 
    timestamp_varchar(30)           2004-02-29 01:02:03.4560 
    varchar(30)_bigint              -268435456 
    varchar(30)_bigint              4026531840 
    varchar(30)_bigint              9223372036854775807 
    varchar(30)_bigint              -1 
    BLOB_ID                         0:1
    81985529216487135 
    varchar(30)_boolean             <true> 
    varchar(30)_char(30)            81985529216487135 
    varchar(30)_date                2004-02-29 
    varchar(30)_decimal(5,2)        80.45 
    varchar(30)_double precision    80.44499999999999 
    varchar(30)_float               80.445 
    varchar(30)_int                 -2147483648 
    varchar(30)_nchar(30)           81985529216487135 
    varchar(30)_numeric(5,2)        80.45 
    varchar(30)_smallint            32767 
    varchar(30)_time                01:02:03.4560 
  """

@pytest.mark.version('>=3.0.6')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


