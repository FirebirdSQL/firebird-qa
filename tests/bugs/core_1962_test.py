#coding:utf-8
#
# id:           bugs.core_1962
# title:        Incorrect extraction of MILLISECONDs
# decription:   
# tracker_id:   CORE-1962
# min_versions: ['2.1.2']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select extract(millisecond from time '01:00:10.5555') EXTRACTED_MS from rdb$database
    union all
    select extract(millisecond from time '00:00:00.0004') from rdb$database
    union all
    select extract(millisecond from time '23:59:59.9995') from rdb$database
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EXTRACTED_MS                    555.5
    EXTRACTED_MS                    0.4
    EXTRACTED_MS                    999.5
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

