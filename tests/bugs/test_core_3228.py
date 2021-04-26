#coding:utf-8
#
# id:           bugs.core_3228
# title:        RIGHT() fails with multibyte text blobs > 1024 chars 
# decription:   
# tracker_id:   CORE-3228
# min_versions: ['2.1.4']
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """with q (s) as (
        select
            cast(
                cast('AAA' as char(1021)) || 'ZZZ'
            as blob sub_type text character set utf8
        )
        from rdb$database
    )
    select right(s, 3) from q;
with q (s) as (
        select
            cast(
                cast('AAA' as char(1022)) || 'ZZZ'
            as blob sub_type text character set utf8
        )
        from rdb$database
    )
    select right(s, 3) from q;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_3228.fdb, User: SYSDBA
SQL> CON> CON> CON> CON> CON> CON> CON> CON>
            RIGHT
=================
              0:3
==============================================================================
RIGHT:
ZZZ
==============================================================================

SQL> CON> CON> CON> CON> CON> CON> CON> CON>
            RIGHT
=================
              0:8
==============================================================================
RIGHT:
ZZZ
==============================================================================

SQL>"""

@pytest.mark.version('>=2.1.4')
def test_core_3228_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

