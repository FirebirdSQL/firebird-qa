#coding:utf-8
#
# id:           bugs.core_4036
# title:        Bugcheck or database corruption when attempting to store long incompressible data into a table
# decription:   
# tracker_id:   CORE-4036
# min_versions: ['2.1.6']
# versions:     2.1.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.6
# resources: None

substitutions_1 = []

init_script_1 = """create table tw(s01 varchar(32600), s02 varchar(32600));
commit;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """insert into tw select rpad('',32600, gen_uuid()),rpad('',32600, gen_uuid()) from rdb$database;
commit;
set heading off;
SELECT count(*) from tw;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """1
"""

@pytest.mark.version('>=2.1.6')
def test_core_4036_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

