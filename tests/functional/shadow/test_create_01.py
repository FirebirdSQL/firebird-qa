#coding:utf-8
#
# id:           functional.shadow.create_01
# title:        CREATE SHADOW
# decription:   CREATE SHADOW
#               
#               Dependencies:
#               CREATE DATABASE
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.shadow.create.create_shadow_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create shadow 1 '$(DATABASE_LOCATION)/test_defaults.shd';
    commit;
    -- SHOW DATABASE -- Removed from here because this test must verify only ability to create shadow.
    set list on;
    set count on;
    select
        --right(trim(rdb$file_name), char_length('test_defaults.shd')) as file_name
        iif( replace(rdb$file_name,'\\','/') containing replace('$(DATABASE_LOCATION)','','/')
             and 
             upper(right( trim(rdb$file_name), char_length('test_defaults.shd') )) = upper('test_defaults.shd')
            ,'OK'
            ,'BAD: ' || rdb$file_name
           ) check_shd_file_name
       ,rdb$file_sequence as file_sequence
       ,rdb$file_start as file_start
       ,rdb$file_length as file_length
       ,rdb$file_flags as file_flags
       ,rdb$shadow_number as shadow_number
    from rdb$files;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CHECK_SHD_FILE_NAME             OK
    FILE_SEQUENCE                   0
    FILE_START                      0
    FILE_LENGTH                     0
    FILE_FLAGS                      1
    SHADOW_NUMBER                   1
    Records affected: 1
  """

@pytest.mark.version('>=3.0')
def test_create_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

