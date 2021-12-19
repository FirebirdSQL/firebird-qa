#coding:utf-8
#
# id:           bugs.core_4452
# title:        Can`t create two collations with different names if autoddl OFF in FB 2.5.3
# decription:
# tracker_id:   CORE-4452
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('COLL-VERSION=\\d{2,}.\\d{2,}', 'COLL-VERSION=111.222')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
show collation;
set autoddl off;
commit;
create collation name_coll for utf8 from unicode CASE INSENSITIVE;
create collation nums_coll for utf8 from unicode CASE INSENSITIVE 'NUMERIC-SORT=1';
commit;
show collation;
drop collation name_coll;
drop collation nums_coll;
commit;
create collation name_coll for utf8 from unicode CASE INSENSITIVE;
create collation nums_coll for utf8 from unicode CASE INSENSITIVE 'NUMERIC-SORT=1';
commit;
show collation;
drop collation name_coll;
drop collation nums_coll;
commit;
show collation;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
NAME_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88'
NUMS_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88;NUMERIC-SORT=1'

NAME_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88'
NUMS_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88;NUMERIC-SORT=1'
  """
expected_stderr_1 = """
There are no user-defined collations in this database
There are no user-defined collations in this database
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

