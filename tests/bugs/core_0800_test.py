#coding:utf-8
#
# id:           bugs.core_0800
# title:        Easy metadata extract improvements
# decription:
#                  Domain DDL: move its CHECK clause from 'create' to 'alter' statement.
#
# tracker_id:   CORE-0800
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    execute block as
    begin
      begin
        execute statement 'drop domain dm_test';
        when any do begin end
      end
      begin
        execute statement 'drop collation name_coll';
        when any do begin end
      end
    end^
    set term ;^
    commit;

    create collation name_coll for utf8 from unicode no pad case insensitive accent insensitive;
    commit;

    create domain dm_test varchar(20)
       character set utf8
       default 'foo'
       not null
       check (value in ('foo', 'rio', 'bar'))
       collate name_coll
       ;
    commit;
  """

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import subprocess
#
#  db_conn.close()
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_file="$(DATABASE_LOCATION)bugs.core_0800.fdb"
#
#  f_extract_meta = open( os.path.join(context['temp_directory'],'tmp_meta_0800_init.sql'), 'w')
#  subprocess.call( [context['isql_path'], dsn, "-x", "-ch", "utf8"],
#                   stdout = f_extract_meta,
#                   stderr = subprocess.STDOUT
#                 )
#  f_extract_meta.close()
#
#  with open( f_extract_meta.name, 'r') as f:
#      for line in f:
#          if 'ALTER DOMAIN' in line.upper():
#              print( line )
#
#  ###############################
#  # Cleanup.
#
#  f_list=[]
#  f_list.append(f_extract_meta)
#
#  for i in range(len(f_list)):
#      if os.path.isfile(f_list[i].name):
#          os.remove(f_list[i].name)
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    ALTER DOMAIN DM_TEST ADD CONSTRAINT
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.extract_meta()
    expected = ''.join([x for x in act_1.clean_stdout.splitlines() if 'ALTER DOMAIN' in x.upper()])
    assert act_1.clean_expected_stdout == expected


