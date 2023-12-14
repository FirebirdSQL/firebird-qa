#coding:utf-8

"""
ID:          issue-6812
ISSUE:       6812
TITLE:       BASE64_ENCODE and HEX_ENCODE can exceed maximum widths for VARCHAR
DESCRIPTION:
FBTEST:      bugs.gh_6812
NOTES:
    [14.12.2023] pzotov
        Added 'SQLSTATE' in substitutions: runtime error must not be filtered out by '?!(...)' pattern
        ("negative lookahead assertion", see https://docs.python.org/3/library/re.html#regular-expression-syntax).
        Added 'combine_output = True' in order to see SQLSTATE if any error occurs.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set sqlda_display on;
    select hex_encode(cast('' as char(32767))) as "enc_01" from rdb$database where 1 <> 1;
    select base64_encode(cast('' as char(32767))) as "enc_02" from rdb$database where 1 <> 1;
"""

act = isql_act('db', test_script, substitutions=[('^((?!(SQLSTATE|sqltype|enc)).)*$', ''), ('[ \t]+', ' ')])

expected_stdout = """
    01: sqltype: 520 BLOB scale: 0 subtype: 1 len: 8 charset: 2 ASCII
    :  name: HEX_ENCODE  alias: enc_01
    01: sqltype: 520 BLOB scale: 0 subtype: 1 len: 8 charset: 2 ASCII
    :  name: BASE64_ENCODE  alias: enc_02
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
