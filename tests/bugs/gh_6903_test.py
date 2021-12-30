#coding:utf-8
#
# id:           bugs.gh_6903
# title:        Unable to create ICU-based collation with locale keywords
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6903
#               
#                   Also: https://github.com/FirebirdSQL/firebird/pull/6914
#                         Allow keywords in locales when creating ICU collations
#               
#                   AFAIU, term 'keywords' here means collation types that can be found here:
#                   https://unicode-org.github.io/icu/userguide/collation/api.html
#               
#                   Checked on WI-T5.0.0.126 (intermediate build, timestamp: 04-aug-2021 12:08); WI-V4.0.1.2556.
#                
# tracker_id:   
# min_versions: ['4.0.1']
# versions:     4.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.1
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    unsuccessful metadata update
    -CREATE COLLATION UNICODE_BAD_01 failed
    -Invalid collation attributes
"""

@pytest.mark.version('>=4.0.1')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
