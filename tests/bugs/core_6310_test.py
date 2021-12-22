#coding:utf-8
#
# id:           bugs.core_6310
# title:        Varchar length limit is not enforced when assigning string with trailing spaces in MBCS
# decription:   
#                  Confirmed bug on 3.0.6.33289, 4.0.0.1954
#                  Checked on 3.0.6.33294, 4.0.0.2000 - works fine.
#                
# tracker_id:   CORE-6310
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select char_length(cast(_utf8 '123         ' as varchar(5) character set utf8)) as char_len from rdb$database; 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CHAR_LEN                        5
"""

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

