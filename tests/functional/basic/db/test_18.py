#coding:utf-8
#
# id:           functional.basic.db.db_18
# title:        Empty DB - RDB$PAGES
# decription:   Check for correct content of RDB$PAGES in empty database.
#               
#               Database is created with 4K pages. We may add other RDB$PAGES tests for different page sizes.
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.basic.db.db_18

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- 30.10.2015. 
    -- 1. Removed from comparison values of RDB$PAGE_NUMBER because its value (can) differ on Win32 vs Nix64.
    -- 2. Added query to select FIELDS list of table because main check does not use asterisk
    -- and we have to know if DDL of table will have any changes in future.

    set blob all;
    set count on;
    set list on;

    -- Query for check whether fields list of table was changed:
    select rf.rdb$field_name
    from rdb$relation_fields rf
    where rf.rdb$relation_name = upper('rdb$pages')
    order by rf.rdb$field_name;

    -- Main test query:
    select rdb$relation_id, rdb$page_sequence, rdb$page_type
    from rdb$pages
    order by 1,2,3;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$FIELD_NAME                  RDB$PAGE_NUMBER                                                                              
    RDB$FIELD_NAME                  RDB$PAGE_SEQUENCE                                                                            
    RDB$FIELD_NAME                  RDB$PAGE_TYPE                                                                                
    RDB$FIELD_NAME                  RDB$RELATION_ID                                                                              

    Records affected: 4

    RDB$RELATION_ID                 0
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   3

    RDB$RELATION_ID                 0
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 0
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 0
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   9

    RDB$RELATION_ID                 1
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 1
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 2
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 2
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 3
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 3
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 4
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 4
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 5
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 5
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 6
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 6
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 7
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 7
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 8
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 8
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 9
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 9
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 10
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 10
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 11
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 11
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 12
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 12
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 13
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 13
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 14
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 14
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 15
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 15
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 16
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 16
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 17
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 17
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 18
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 18
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 19
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 19
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 20
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 20
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 21
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 21
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 22
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 22
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 23
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 23
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 24
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 24
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 25
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 25
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 26
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 26
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 27
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 27
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 28
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 28
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 29
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 29
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 30
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 30
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 31
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 31
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 32
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 32
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 42
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 42
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 45
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 45
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 47
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 47
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    Records affected: 74
  """

@pytest.mark.version('>=3.0,<4.0')
def test_db_18_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    -- 30.10.2015. 
    -- 1. Removed from comparison values of RDB$PAGE_NUMBER because its value (can) differ on Win32 vs Nix64.
    -- 2. Added query to select FIELDS list of table because main check does not use asterisk
    -- and we have to know if DDL of table will have any changes in future.

    set blob all;
    set count on;
    set list on;

    -- Query for check whether fields list of table was changed:
    select rf.rdb$field_name
    from rdb$relation_fields rf
    where rf.rdb$relation_name = upper('rdb$pages')
    order by rf.rdb$field_name;

    -- Main test query:
    select rdb$relation_id, rdb$page_sequence, rdb$page_type
    from rdb$pages
    order by 1,2,3;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$FIELD_NAME                  RDB$PAGE_NUMBER                                                                                                                                                                                                                                             
    RDB$FIELD_NAME                  RDB$PAGE_SEQUENCE                                                                                                                                                                                                                                           
    RDB$FIELD_NAME                  RDB$PAGE_TYPE                                                                                                                                                                                                                                               
    RDB$FIELD_NAME                  RDB$RELATION_ID                                                                                                                                                                                                                                             

    Records affected: 4


    RDB$RELATION_ID                 0
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   3

    RDB$RELATION_ID                 0
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 0
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 0
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   9

    RDB$RELATION_ID                 1
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 1
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 2
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 2
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 3
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 3
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 4
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 4
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 5
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 5
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 6
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 6
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 7
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 7
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 8
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 8
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 9
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 9
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 10
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 10
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 11
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 11
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 12
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 12
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 13
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 13
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 14
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 14
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 15
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 15
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 16
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 16
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 17
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 17
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 18
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 18
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 19
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 19
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 20
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 20
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 21
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 21
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 22
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 22
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 23
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 23
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 24
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 24
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 25
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 25
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 26
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 26
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 27
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 27
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 28
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 28
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 29
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 29
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 30
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 30
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 31
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 31
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 32
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 32
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 42
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 42
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 45
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 45
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 47
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 47
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 51
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 51
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    RDB$RELATION_ID                 52
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   4

    RDB$RELATION_ID                 52
    RDB$PAGE_SEQUENCE               0
    RDB$PAGE_TYPE                   6

    Records affected: 78
  """

@pytest.mark.version('>=4.0')
def test_db_18_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

