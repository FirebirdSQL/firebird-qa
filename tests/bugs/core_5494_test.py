#coding:utf-8

"""
ID:          issue-5763
ISSUE:       5763
TITLE:       Creating a column of type BLOB SUB_TYPE BINARY fails with a Token unknown
DESCRIPTION:
JIRA:        CORE-5494
FBTEST:      bugs.core_5494
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
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
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

