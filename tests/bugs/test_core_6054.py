#coding:utf-8
#
# id:           bugs.core_6054
# title:        Random crash 64bit fb_inet_server. Possible collation issue
# decription:   
#                  Confirmed bug on WI-V2.5.9.27129. Major versions 3.x and 4.x was not affected.
#                  Works fine on WI-V2.5.9.27134.
#                
# tracker_id:   CORE-6054
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = [('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+', '-At line: column:')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table c (id int, f1 varchar(32) character set win1251 collate win1251);
    select * from c where f2 collate win1251_ua = 'x';
    set count on;
    select * from c where f1 = _utf8 'x';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42S22
    Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -F2
    -At line: column:
  """

@pytest.mark.version('>=2.5.9')
def test_core_6054_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

