#coding:utf-8

"""
ID:          issue-6903
ISSUE:       6903
TITLE:       Unable to create ICU-based collation with locale keywords
DESCRIPTION:
FBTEST:      bugs.gh_6903
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- should PASS:
    create collation unicode_txt_01 for utf8 from unicode
      pad space
      case sensitive
      accent sensitive
      'LOCALE=de-u-co-phonebk-ka-shifted'
    ;

    -- should PASS:
    create collation unicode_txt_02 for utf8 from unicode
      'locale=en-u-kr-grek-latn-digit'
    ;

    -- should PASS:
    create collation unicode_txt_03 for utf8 from unicode
      pad space
      case sensitive
      accent sensitive
      'LOCALE=el@colCaseFirst=upper'
    ;

    -- should FAIL!
    -- See: https://github.com/FirebirdSQL/firebird/pull/6914
    -- Note by Adriano "I tried ... it worked, but should not"
    create collation unicode_bad_01 for utf8 from unicode
      'LOCALE=pt_BRx'
    ;

"""

act = isql_act('db', test_script, substitutions=[('[ \t]+', ' ')])

expected_stderr = """
    Statement failed, SQLSTATE = HY000
    unsuccessful metadata update
    -CREATE COLLATION UNICODE_BAD_01 failed
    -Invalid collation attributes
"""

@pytest.mark.version('>=4.0.1')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
