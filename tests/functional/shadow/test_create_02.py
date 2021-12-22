#coding:utf-8
#
# id:           functional.shadow.create_02
# title:        CREATE SHADOW
# decription:   
#                   CREATE SHADOW
#               
#                   Dependencies:
#                   CREATE DATABASE
#                 
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         functional.shadow.create.create_shadow_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create shadow 1 manual conditional '$(DATABASE_LOCATION)TEST.SHD' file '$(DATABASE_LOCATION)TEST.S00' starting at page 1000;
    commit;
    set list on;
    set count on;
    select 
        right(trim(rdb$file_name), char_length('test.s??')) as file_name
       ,rdb$file_sequence as file_sequence
       ,rdb$file_start as file_start
       ,rdb$file_length as file_length
       ,rdb$file_flags as file_flags
       ,rdb$shadow_number as shadow_number
    from rdb$files;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    FILE_NAME                       TEST.SHD
    FILE_SEQUENCE                   0
    FILE_START                      0
    FILE_LENGTH                     0
    FILE_FLAGS                      5
    SHADOW_NUMBER                   1

    FILE_NAME                       TEST.S00
    FILE_SEQUENCE                   1
    FILE_START                      1000
    FILE_LENGTH                     0
    FILE_FLAGS                      5
    SHADOW_NUMBER                   1

    Records affected: 2
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

