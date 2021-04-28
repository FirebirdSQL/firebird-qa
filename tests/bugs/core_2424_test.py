#coding:utf-8
#
# id:           bugs.core_2424
# title:        Make CREATE VIEW infer column names for views involving a GROUP BY clause or derived table
# decription:   
# tracker_id:   CORE-2424
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """create view V as select d.rdb$relation_id from rdb$database d group by d.rdb$relation_id;
show view v;
recreate view V as select a from (select 1 a from rdb$database);
show view v;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_2424.fdb, User: SYSDBA
SQL> SQL> RDB$RELATION_ID                 SMALLINT Expression
View Source:
==== ======
 select d.rdb$relation_id from rdb$database d group by d.rdb$relation_id
SQL> SQL> A                               INTEGER Expression
View Source:
==== ======
 select a from (select 1 a from rdb$database)
SQL>"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

