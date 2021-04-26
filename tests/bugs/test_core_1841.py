#coding:utf-8
#
# id:           bugs.core_1841
# title:        If some VIEW used derived tables and long table namesliases, It is possible to overflow RDB$VIEW_RELATIONS.RDB$CONTEXT_NAME
# decription:   
# tracker_id:   CORE-1841
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_1841-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create view x (id) as
select RDB$RELATION_ID
 from (select * from RDB$DATABASE long_alias_long_alias_1) long_alias_long_alias_2;
COMMIT;
SHOW VIEW x;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID                              SMALLINT Expression
View Source:
==== ======

select RDB$RELATION_ID
 from (select * from RDB$DATABASE long_alias_long_alias_1) long_alias_long_alias_2
"""

@pytest.mark.version('>=2.5.0')
def test_core_1841_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

