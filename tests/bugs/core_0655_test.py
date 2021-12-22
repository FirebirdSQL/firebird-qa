#coding:utf-8
#
# id:           bugs.core_0655
# title:        Blob Type 1 compatibility with VarChar
# decription:   Blob Sub-Type 1 (text) column treated in the same manner as a VarChar column
#               for assignments, conversions, cast, lower, upper, trim, concatenate and substring
# tracker_id:   CORE-655
# min_versions: ['2.1.0']
# versions:     2.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (f1 BLOB SUB_TYPE 1 SEGMENT SIZE 80);
insert into t1 values ('Firebird ');

"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select cast(lower(f1) as varchar(20)) lf1, cast(upper(f1) as varchar(20)) uf1, cast(trim(f1)||'2.1'  as varchar(20))tf1, cast(f1||'2.1' as varchar(20)) cf1, cast(substring(f1 from 1 for 5) as varchar(20)) sf1 from t1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\fbtest\\tmp\\bugs.core_655.fdb, User: SYSDBA
SQL>
LF1                  UF1                  TF1                  CF1                  SF1
==================== ==================== ==================== ==================== ====================
firebird             FIREBIRD             Firebird2.1          Firebird 2.1         Fireb

SQL>"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

