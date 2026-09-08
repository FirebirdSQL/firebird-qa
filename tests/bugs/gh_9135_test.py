#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9135
TITLE:       Remove limit for usage of blob subtypes in user objects
DESCRIPTION:
    Test creates a view with column based on rdb$formats.rdb$descriptor which has sub_type = 6.
    Query to this view should return readable content - as for case when data from rdb$formats is directly obtained.
NOTES:
    [08.09.2026] pzotov
    Prior this ticket was fixed, an attempt to create view from test script failed with:
        unsuccessful metadata update
        -RECREATE VIEW V_CHECK failed
        -Dynamic SQL Error
        -SQL error code = -204
        -Data type unknown
        -Blob sub_types bigger than 1 (text) are for internal use only
    An attampt to cast blob to sub_type = text:
        recreate view v_check as
        select cast(rdb$descriptor as blob sub_type text) as rdb_descr
        from rdb$formats ...
    - caused to unreadable content of outcome (all newline characters were removed).
    Discussed with dimitr, letters since 03.12.2025 11:52.
    See also message from Dmitry Sibiryakov, 01.03.2026 19:53.
    Checked on 6.0.0.2174-6b72815.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    set blob all;
    recreate table test (a smallint, b int, c bigint, d int128);
    commit;
    recreate view v_check as ---------------  [ 1 ]
    select rf.rdb$descriptor as blob_id
    from rdb$formats rf
    join rdb$relations rr on rf.rdb$relation_id = rr.rdb$relation_id
    where rr.rdb$relation_name = upper('test')
    ;
    select v.* from v_check as v;
"""

substitutions = [('[ \t]+', ' '), ('BLOB_ID.*', 'BLOB_ID')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    BLOB_ID
    Fields:
     id offset type           length sub_type flags
    --- ------ -------------- ------ -------- -----
      0      4  8 SHORT            2        0  0x00
      1      8  9 LONG             4        0  0x00
      2     16 19 BIGINT           8        0  0x00
      3     24 24 INT128          16        0  0x00
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
