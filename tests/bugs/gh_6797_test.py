#coding:utf-8

"""
ID:          issue-6797
ISSUE:       6797
TITLE:       Functions DECRYPT and RSA_DECRYPT return VARCHAR CHARACTER SET NONE instead
  of VARBINARY (VARCHAR CHARACTER SET OCTETS)
DESCRIPTION:
NOTES:
  As of current FB 4.x doc, following is wrong: "Functions return ... *varbinary* for all other types."
  (see note by Alex in the tracker, 11.05.2021 11:17).
FBTEST:      bugs.gh_6797
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set blob all;
    set list on;
    set sqlda_display on;
    set planonly;
    select
        decrypt(cast('' as varchar(1)) using aes mode ofb key '0123456701234567' iv '1234567890123456') as decrypt_vchr
       ,decrypt(cast('' as blob) using aes mode ofb key '0123456701234567' iv '1234567890123456') as decrypt_blob
    from rdb$database;
"""

act = isql_act('db', test_script, substitutions=[('^((?!(sqltype)).)*$', ''), ('[ \t]+', ' ')])

expected_stdout = """
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 1 charset: 1 OCTETS
    02: sqltype: 520 BLOB scale: 0 subtype: 0 len: 8
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
