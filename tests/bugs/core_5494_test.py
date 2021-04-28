#coding:utf-8
#
# id:           bugs.core_5494
# title:        Creating a column of type BLOB SUB_TYPE BINARY fails with a Token unknown
# decription:   
#                  Confirmed compilation problem on WI-T4.0.0.546.
#                  Checked on WI-T4.0.0.549 -- all OK.
#                
# tracker_id:   CORE-5494
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
    set bail on;
    recreate table test (
      c1 binary(8),
      v1 varbinary(8),
      b1 blob sub_type binary
    );

    insert into test(c1, b1) values('', '');
    update test set c1 = rdb$db_key, v1 = rdb$db_key, b1 = rpad('',32765,gen_uuid());

    set sqlda_display on;
    set planonly;
    select * from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 0

    PLAN (TEST NATURAL)

    OUTPUT message field count: 3
    01: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 8 charset: 1 OCTETS
      :  name: C1  alias: C1
      : table: TEST  owner: SYSDBA
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 8 charset: 1 OCTETS
      :  name: V1  alias: V1
      : table: TEST  owner: SYSDBA
    03: sqltype: 520 BLOB Nullable scale: 0 subtype: 0 len: 8
      :  name: B1  alias: B1
      : table: TEST  owner: SYSDBA
   """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

