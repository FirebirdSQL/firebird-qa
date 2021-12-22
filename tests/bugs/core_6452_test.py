#coding:utf-8
#
# id:           bugs.core_6452
# title:        SIMILAR TO leads to an infinite loop
# decription:   
#                  One more test to check 're2' library.
#                  Confirmed on 3.0.8, no problems with 4.0 (checked on 4.0.0.2296).
#                
# tracker_id:   CORE-6452
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    select
      1
    from
      RDB$DATABASE
    where
      '<licenc>
            <items>
                <item title="CallCenter" value="false"/>
                <item title="CRM" value="false"/>
                <item title="Securities" value="false"/>
                <item title="Credits" value="false"/>
                <item title="Registry" value="true"/>
                <item title="Campaign" value="true"/>
                <item title="Damages" value="false"/>
                <item title="Prints" value="false"/>
                <item title="Online" value="true"/>
             </items>
       </licenc>' similar to '%title="_{3,40}" value="true"%';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

