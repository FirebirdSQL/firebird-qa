#coding:utf-8
#
# id:           bugs.core_5064
# title:        Add datatypes (VAR)BINARY(n) and BINARY VARYING(n) as alias for (VAR)CHAR(n) CHARACTER SET OCTETS
# decription:   
#                
# tracker_id:   CORE-5064
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(x binary(8), y varbinary(8));
    set list on;
    set sqlda_display on;
    
    -- Check that new datatypes can be used in SQL:
    select rdb$db_key,t.* from test t;

    -- Check that new datatypes can be used in PSQL:
    set term ^; 
    execute block returns(x binary(8), y varbinary(8)) as 
    begin 
        select rdb$db_key,rdb$db_key 
        from rdb$database where 1=0 
        into x,y; 
        suspend; 
    end^ 
    set term ;^

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 0

    OUTPUT message field count: 3
    01: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 8 charset: 1 OCTETS
      :  name: DB_KEY  alias: DB_KEY
      : table: TEST  owner: SYSDBA
    02: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 8 charset: 1 OCTETS
      :  name: X  alias: X
      : table: TEST  owner: SYSDBA
    03: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 8 charset: 1 OCTETS
      :  name: Y  alias: Y
      : table: TEST  owner: SYSDBA

    INPUT message field count: 0

    OUTPUT message field count: 2
    01: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 8 charset: 1 OCTETS
      :  name: X  alias: X
      : table:   owner:
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 8 charset: 1 OCTETS
      :  name: Y  alias: Y
      : table:   owner:

    X                               <null>
    Y                               <null>
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

