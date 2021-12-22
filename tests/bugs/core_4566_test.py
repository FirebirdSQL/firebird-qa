#coding:utf-8
#
# id:           bugs.core_4566
# title:        Incorrect size of the output parameter/argument when execute block, procedure or function use system field in metadata charset
# decription:   
# tracker_id:   CORE-4566
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='WIN1251', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create or alter function get_mnemonic (
        afield_name type of column rdb$types.rdb$field_name,
        atype type of column rdb$types.rdb$type)
    returns type of column rdb$types.rdb$type_name
    as
    begin
      return (select rdb$type_name
              from rdb$types
              where 
                  rdb$field_name = :afield_name
                  and rdb$type = :atype
              order by rdb$type_name
             );
    end 
    ^
    set term ;^
    commit;
    
    set list on;

    select get_mnemonic('MON$SHUTDOWN_MODE', 1) as mnemonic from rdb$database;
    --select cast(get_mnemonic('MON$SHUTDOWN_MODE', 1) as varchar(100)) as mnemonic from rdb$database;
    
    set term ^;
    execute block returns (FIELD_NAME RDB$FIELD_NAME) as
    begin
      for select rdb$type_name
          from rdb$types
          where rdb$type_name starting with 'BLOB_FILTER'
          order by rdb$type_name
          rows 1
          into field_name
      do
        suspend;
    end
    ^
    set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MNEMONIC                        MULTI_USER_SHUTDOWN            
    FIELD_NAME                      BLOB_FILTER                    
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

