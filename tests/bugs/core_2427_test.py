#coding:utf-8
#
# id:           bugs.core_2427
# title:        ALTER VIEW doesn't clear dependencies on old views
# decription:   
# tracker_id:   CORE-2427
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """create view v1 (n) as select 'ABC' from rdb$database;
create view v3 (n) as select substring(lower(n) from 1) from v1;
create view newv (n) as select 'XYZ' from rdb$database;
alter view v3 (n) as select substring(lower(n) from 1) from newv;
drop view v1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.execute()

