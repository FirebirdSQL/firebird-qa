#coding:utf-8
#
# id:           bugs.gh_6915
# title:        Allow attribute DISABLE-COMPRESSIONS in UNICODE collations
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6915
#               
#                   NOTE: only ability to use 'DISABLE-COMPRESSION' in attributes list is checked here.
#                   Performance comparison with and without this attribute will be checked in separate test.
#               
#                   Checked on 5.0.0.126 (intermediate build, timestamp: 04-aug-2021 12:08); WI-V4.0.1.2556.
#                
# tracker_id:   
# min_versions: ['4.0.1']
# versions:     4.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.1
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create collation coll_cs_dc
       for UTF8  
       from UNICODE  
       case sensitive  
       'LOCALE=cs_CZ;DISABLE-COMPRESSIONS=1'
    ;

    create collation coll_ci_dc
       for UTF8  
       from UNICODE  
       case insensitive  
       'LOCALE=cs_CZ;DISABLE-COMPRESSIONS=1'
    ;

    create collation coll_cs_dc_ns
       for UTF8  
       from UNICODE  
       case sensitive  
       'LOCALE=cs_CZ;DISABLE-COMPRESSIONS=1;NUMERIC-SORT=1'
    ;

    create collation coll_ci_dc_ns
       for UTF8  
       from UNICODE  
       case insensitive  
       'LOCALE=cs_CZ;DISABLE-COMPRESSIONS=1;NUMERIC-SORT=1'
    ;
  
  
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

@pytest.mark.version('>=4.0.1')
def test_1(act_1: Action):
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
