#coding:utf-8
#
# id:           bugs.core_2019
# title:        UTF-8 conversion error (string truncation)
# decription:   
# tracker_id:   CORE-2019
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """recreate table test (
 column1 varchar(10) character set none collate none );

insert into test values ('1234567890');
commit;
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select coalesce(column1, '') from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
COALESCE
==========
1234567890

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

