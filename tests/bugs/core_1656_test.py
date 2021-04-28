#coding:utf-8
#
# id:           bugs.core_1656
# title:        Ability to format UUID from char(16) OCTETS to human readable form and vice versa
# decription:   
# tracker_id:   CORE-1656
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select uuid_to_char(char_to_uuid('93519227-8D50-4E47-81AA-8F6678C096A1')) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
UUID_TO_CHAR
====================================
93519227-8D50-4E47-81AA-8F6678C096A1

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

