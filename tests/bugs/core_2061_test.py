#coding:utf-8
#
# id:           bugs.core_2061
# title:        ALTER VIEW WITH CHECK OPTION crashes the engin
# decription:   
# tracker_id:   CORE-2061
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """create or alter view v as select * from rdb$database where 1 = 0 with check option;
alter view v as select * from rdb$database where 1 = 1 with check option;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.execute()

