#coding:utf-8
#
# id:           bugs.core_3335
# title:        Wrong results (internal wrapping occured) for the multi-byte blob SUBSTRING function and its boundary arguments
# decription:   
# tracker_id:   CORE-3335
# min_versions: ['2.1.5']
# versions:     2.1.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select substring(cast('abcdef' as blob sub_type text character set utf8)
from 1 for 2147483647) from rdb$database;
select substring(cast('abcdef' as blob sub_type text character set utf8)
from 2 for 2147483647) from rdb$database;
select substring(cast('abcdef' as blob sub_type text character set utf8)
from 3 for 2147483647) from rdb$database;
select substring(cast('abcdef' as blob sub_type text character set utf8)
from 3 for 2147483646) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btestnew	mpugs.core_3335.fdb, User: SYSDBA
SQL> CON>
        SUBSTRING
=================
              0:2
==============================================================================
SUBSTRING:
abcdef
==============================================================================

SQL> CON>
        SUBSTRING
=================
              0:6
==============================================================================
SUBSTRING:
bcdef
==============================================================================

SQL> CON>
        SUBSTRING
=================
              0:a
==============================================================================
SUBSTRING:
cdef
==============================================================================

SQL> CON>
        SUBSTRING
=================
              0:e
==============================================================================
SUBSTRING:
cdef
==============================================================================

SQL>"""

@pytest.mark.version('>=2.1.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

