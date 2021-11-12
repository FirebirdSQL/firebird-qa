#coding:utf-8
#
# id:           bugs.core_1760
# title:        Support hex numeric and string literals
# decription:
#                   See doc\\sql.extensions\\README.hex_literals.txt
#
#                   REFACTORED 27.02.2020:
#                   1) all SQL code was moved into separate file: $files_location/core_1760.sql because it is common for all major FB versions;
#                   2) added examples from https://firebirdsql.org/refdocs/langrefupd25-bigint.html (see core_1760.sql);
#                   3) added check for output datatypes (sqlda_display).
#
#                   Checked on:
#                       4.0.0.1789 SS: 1.458s.
#                       3.0.6.33259 SS: 0.805s.
#                       2.5.9.27149 SC: 0.397s.
#
# tracker_id:   CORE-1760
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('.*At line.*', ''), ('-Token unknown.*', '-Token unknown')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    -- binary literal ::=  { x | X } <quote> [ { <hexit> <hexit> }... ] <quote>

    select x'1' from rdb$database; -- raises: token unknown because length is odd

    select x'11' from rdb$database; -- must raise: token unknown because length is odd

    select x'0123456789' from rdb$database;

    select x'01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789' from rdb$database;

    -- must raise: token unknown because last char is not hexit
    select x'0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678x' from rdb$database;

    select uuid_to_char(x'BA1749B583BF9146B360F54E25FE583E') from rdb$database;


    -- ##############################################################################

    -- Numeric literal: { 0x | 0X } <hexit> [ <hexit>... ]
    -- https://firebirdsql.org/refdocs/langrefupd25-bigint.html
    recreate view v_test as
    select
        +-0x1              "-1(a)"
       ,-+-0xf             "+15"
       ,0x7FFF             "32767"
       ,0x8000             "32768"
       ,0xFFFF             "65535"
       ,0x10000            "65536(a)"
       ,0x000000000010000  "65536(b)"
       ,0x80000000         "-2147483648"
       ,0x080000000        "+2147483648(a)"
       ,0x000000080000000  "+2147483648(b)"
       ,0XFFFFFFFF         "-1(b)"
       ,0X0FFFFFFFF        "+4294967295"
       ,0x100000000        "+4294967296(a)"
       ,0x0000000100000000 "+4294967296(b)"
       ,0X7FFFFFFFFFFFFFFF "9223372036854775807"
       ,0x8000000000000000 "-9223372036854775808"
       ,0x8000000000000001 "-9223372036854775807"
       ,0x8000000000000002 "-9223372036854775806"
       ,0xffffffffffffffff "-1(c)"
    from rdb$database;

    select * from v_test;

    -- If the number of <hexit> is greater than 8, the constant data type is a signed BIGINT
    -- If it's less or equal than 8, the data type is a signed INTEGER
    set sqlda_display on;
    select * from v_test rows 0;
    set sqlda_display off;
"""

#---
#
#  import os
#  import sys
#  import subprocess
#  from fdb import services
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  #--------------------------------------------
#
#  def flush_and_close(file_handle):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb'):
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#
#  #--------------------------------------------
#
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if os.path.isfile( f_names_list[i]):
#              os.remove( f_names_list[i] )
#  #--------------------------------------------
#
#  db_conn.close()
#
#  sql_chk = os.path.join(context['files_location'],'core_1760.sql')
#
#  f_sql_log = open( os.path.join(context['temp_directory'],'tmp_core_1760.log'), 'w', buffering = 0)
#  f_sql_err = open( os.path.join(context['temp_directory'],'tmp_core_1760.err'), 'w', buffering = 0)
#
#  subprocess.call( [ context['isql_path'], dsn, '-q', '-i', sql_chk ], stdout = f_sql_log, stderr = f_sql_err)
#
#  flush_and_close( f_sql_log )
#  flush_and_close( f_sql_err )
#
#  for f in (f_sql_log, f_sql_err):
#      with open( f.name,'r') as g:
#          for line in g:
#              if line.strip():
#                  print( ('STDOUT: ' if f == f_sql_log else 'STDERR: ') + line )
#
#  cleanup( (f_sql_log.name, f_sql_err.name) )
#
#---

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
CONSTANT                        11
CONSTANT                        0123456789
CONSTANT                        01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
UUID_TO_CHAR                    BA1749B5-83BF-9146-B360-F54E25FE583E
-1(a)                           -1
+15                             15
32767                           32767
32768                           32768
65535                           65535
65536(a)                        65536
65536(b)                        65536
-2147483648                     -2147483648
+2147483648(a)                  2147483648
+2147483648(b)                  2147483648
-1(b)                           -1
+4294967295                     4294967295
+4294967296(a)                  4294967296
+4294967296(b)                  4294967296
9223372036854775807             9223372036854775807
-9223372036854775808            -9223372036854775808
-9223372036854775807            -9223372036854775807
-9223372036854775806            -9223372036854775806
-1(c)                           -1
INPUT message field count: 0
OUTPUT message field count: 19
01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
  :  name: -1(a)  alias: -1(a)
  : table: V_TEST  owner: SYSDBA
02: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
  :  name: +15  alias: +15
  : table: V_TEST  owner: SYSDBA
03: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
  :  name: 32767  alias: 32767
  : table: V_TEST  owner: SYSDBA
04: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
  :  name: 32768  alias: 32768
  : table: V_TEST  owner: SYSDBA
05: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
  :  name: 65535  alias: 65535
  : table: V_TEST  owner: SYSDBA
06: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
  :  name: 65536(a)  alias: 65536(a)
  : table: V_TEST  owner: SYSDBA
07: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: 65536(b)  alias: 65536(b)
  : table: V_TEST  owner: SYSDBA
08: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
  :  name: -2147483648  alias: -2147483648
  : table: V_TEST  owner: SYSDBA
09: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: +2147483648(a)  alias: +2147483648(a)
  : table: V_TEST  owner: SYSDBA
10: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: +2147483648(b)  alias: +2147483648(b)
  : table: V_TEST  owner: SYSDBA
11: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
  :  name: -1(b)  alias: -1(b)
  : table: V_TEST  owner: SYSDBA
12: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: +4294967295  alias: +4294967295
  : table: V_TEST  owner: SYSDBA
13: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: +4294967296(a)  alias: +4294967296(a)
  : table: V_TEST  owner: SYSDBA
14: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: +4294967296(b)  alias: +4294967296(b)
  : table: V_TEST  owner: SYSDBA
15: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: 9223372036854775807  alias: 9223372036854775807
  : table: V_TEST  owner: SYSDBA
16: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: -9223372036854775808  alias: -9223372036854775808
  : table: V_TEST  owner: SYSDBA
17: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: -9223372036854775807  alias: -9223372036854775807
  : table: V_TEST  owner: SYSDBA
18: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: -9223372036854775806  alias: -9223372036854775806
  : table: V_TEST  owner: SYSDBA
19: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  :  name: -1(c)  alias: -1(c)
  : table: V_TEST  owner: SYSDBA
"""

expected_stderr_1 = """
Statement failed, SQLSTATE = 42000
Dynamic SQL Error
-SQL error code = -104
-Token unknown - line 1, column 9
-'1'

Statement failed, SQLSTATE = 42000
Dynamic SQL Error
-SQL error code = -104
-Token unknown - line 1, column 9
-'0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678x'
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
    assert act_1.clean_stderr == act_1.clean_expected_stderr


