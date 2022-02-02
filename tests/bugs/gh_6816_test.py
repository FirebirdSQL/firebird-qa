#coding:utf-8

"""
ID:          issue-6816
ISSUE:       6816
TITLE:       Illegal output length in base64/hex_encode/decode functions
DESCRIPTION:
FBTEST:      bugs.gh_6816
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set sqlda_display on;
    set list on;
    select hex_encode(cast('' as varbinary(5))), base64_encode(cast('' as varbinary(5))) from rdb$database where 1 <> 1;
    -- produces lengths 14 & 12 with 10 & 8 expected
    select base64_decode(cast('' as varchar(4) character set utf8)), hex_decode(cast('' as varchar(4) character set utf8)) from rdb$database where 1<>1;
    -- produces lengths 12 & 8 with 3 & 2 expected
"""

act = isql_act('db', test_script, substitutions=[('^((?!(sqltype)).)*$', ''), ('[ \t]+', ' ')])

expected_stdout = """
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 10 charset: 2 ASCII
    02: sqltype: 448 VARYING scale: 0 subtype: 0 len: 8 charset: 2 ASCII
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 3 charset: 1 OCTETS
    02: sqltype: 448 VARYING scale: 0 subtype: 0 len: 2 charset: 1 OCTETS
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
