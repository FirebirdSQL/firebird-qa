#coding:utf-8

"""
ID:          shadow.create-01
TITLE:       CREATE SHADOW
DESCRIPTION:
FBTEST:      functional.shadow.create_01
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create shadow 1 '$(DATABASE_LOCATION)test_defaults.shd';
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

act = isql_act('db', test_script)

expected_stdout = """
    CHECK_SHD_FILE_NAME             OK
    FILE_SEQUENCE                   0
    FILE_START                      0
    FILE_LENGTH                     0
    FILE_FLAGS                      1
    SHADOW_NUMBER                   1
    Records affected: 1
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
