#coding:utf-8
#
# id:           bugs.core_4557
# title:        FB 3.0 crashes on EXIT (or QUIT) command if use UTF8-collation + create domain based on it + issue SHOW DOMAIN
# decription:   
# tracker_id:   CORE-4557
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
  create collation name_coll for utf8 from unicode CASE INSENSITIVE;
  create collation nums_coll for utf8 from unicode CASE INSENSITIVE 'NUMERIC-SORT=1';
  commit;
  create domain dm_name as varchar(80) character set utf8 collate name_coll;
  create domain dm_nums as varchar(20) character set utf8 collate nums_coll;
  commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
  show domain; -- FB crashes if this will be uncommented
  exit; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  DM_NAME                                DM_NUMS
  """

@pytest.mark.version('>=3.0,<4.0')
def test_core_4557_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """
  create collation name_coll for utf8 from unicode CASE INSENSITIVE;
  create collation nums_coll for utf8 from unicode CASE INSENSITIVE 'NUMERIC-SORT=1';
  commit;
  create domain dm_name as varchar(80) character set utf8 collate name_coll;
  create domain dm_nums as varchar(20) character set utf8 collate nums_coll;
  commit;
  """

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
  show domain; -- FB crashes if this will be uncommented
  exit; 
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    DM_NAME
    DM_NUMS
  """

@pytest.mark.version('>=4.0')
def test_core_4557_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

