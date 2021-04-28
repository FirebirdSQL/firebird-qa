#coding:utf-8
#
# id:           bugs.core_3312
# title:        Sub-optimal join plan when the slave table depends on the master one via the OR predicate
# decription:   
# tracker_id:   CORE-3312
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLANONLY ON;
select *
from rdb$relations r
  join rdb$security_classes sc
    on (r.rdb$security_class = sc.rdb$security_class
      or r.rdb$default_class = sc.rdb$security_class);
select *
from rdb$relations r
  join rdb$security_classes sc
    on (r.rdb$security_class = sc.rdb$security_class and r.rdb$relation_id = 0)
      or (r.rdb$default_class = sc.rdb$security_class and r.rdb$relation_id = 1);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\Users\\win7\\Firebird_tests\\fbt-repository\\tmp\\bugs.core_3312.fdb, User: SYSDBA
SQL> SQL> CON> CON> CON> CON>
PLAN JOIN (R NATURAL, SC INDEX (RDB$INDEX_7, RDB$INDEX_7))
SQL> CON> CON> CON> CON>
PLAN JOIN (R INDEX (RDB$INDEX_1, RDB$INDEX_1), SC INDEX (RDB$INDEX_7, RDB$INDEX_7))
SQL>"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

