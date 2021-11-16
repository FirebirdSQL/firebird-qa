#coding:utf-8
#
# id:           bugs.core_2606
# title:        Multibyte CHAR value requested as VARCHAR is returned with padded spaces
# decription:
# tracker_id:   CORE-2606
# min_versions: ['3.0']
# versions:     3.0
# qmid:

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#
#  db_conn.close()
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  sql_cmd='''
#  set list on;
#
#  select s.rdb$character_set_name as client_charset
#  from mon$attachments a
#  join rdb$character_sets s on a.mon$character_set_id = s.rdb$character_set_id
#  where a.mon$attachment_id=current_connection;
#
#  --set sqlda_display on;
#  --set planonly;
#  --set echo on;
#
#  select cast('A' as char character set utf8) || '.' as char1_utf8 from rdb$database;
#  select cast('A' as varchar(1) character set utf8) || '.' as varc1_utf8 from rdb$database;
#  select cast('A' as char character set ascii) || '.' char1_ascii from rdb$database;
#  select cast('A' as varchar(1) character set ascii) || '.' varc1_ascii from rdb$database;
#  '''
#
#  # Wrong result was encountered only in FB 1.5.6, for cast('A' as Char charset utf8 / ascii), on any client charset.
#  # Varchar always returns expected output.
#
#  runProgram('isql',['-q', '-ch', 'UTF8', dsn], sql_cmd)
#  runProgram('isql',['-q', '-ch', 'SJIS_0208', dsn], sql_cmd)
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

test_script_1 = """
set list on;

select s.rdb$character_set_name as client_charset
from mon$attachments a
join rdb$character_sets s on a.mon$character_set_id = s.rdb$character_set_id
where a.mon$attachment_id=current_connection;

--set sqlda_display on;
--set planonly;
--set echo on;

select cast('A' as char character set utf8) || '.' as char1_utf8 from rdb$database;
select cast('A' as varchar(1) character set utf8) || '.' as varc1_utf8 from rdb$database;
select cast('A' as char character set ascii) || '.' char1_ascii from rdb$database;
select cast('A' as varchar(1) character set ascii) || '.' varc1_ascii from rdb$database;
"""

expected_stdout_1_a = """
    CLIENT_CHARSET                  UTF8
    CHAR1_UTF8                      A.
    VARC1_UTF8                      A.
    CHAR1_ASCII                     A.
    VARC1_ASCII                     A.
"""

expected_stdout_1_b = """
    CLIENT_CHARSET                  SJIS_0208
    CHAR1_UTF8                      A.
    VARC1_UTF8                      A.
    CHAR1_ASCII                     A.
    VARC1_ASCII                     A.
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1_a
    act_1.script = test_script_1
    act_1.charset = 'UTF8'
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1_b
    act_1.script = test_script_1
    act_1.charset = 'SJIS_0208'
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout



