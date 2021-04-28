#coding:utf-8
#
# id:           bugs.core_0696
# title:        User Account maintanance in SQL
# decription:   
# tracker_id:   CORE-696
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

test_script_1 = """CREATE USER alex PASSWORD 'test';
COMMIT;
ALTER USER alex FIRSTNAME 'Alex' LASTNAME 'Peshkov';
COMMIT;
ALTER USER alex PASSWORD 'IdQfA';
COMMIT;
DROP USER alex;
COMMIT;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.execute()

