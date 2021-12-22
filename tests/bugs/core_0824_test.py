#coding:utf-8
#
# id:           bugs.core_0824
# title:        accent ignoring collation for unicode
# decription:   
# tracker_id:   CORE-824
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT IIF('eeaauoeeeaauo' = 'ÉÈÀÂÛÔÊéèàâûô' COLLATE UNICODE_CI_AI ,'true','false'),'true','''eeaauoeeeaauo'' = ''ÉÈÀÂÛÔÊéèàâûô'' COLLATE UNICODE_CI_AI' FROM RDB$DATABASE;
SELECT IIF('EEAAUOEEEAAUO' = 'ÉÈÀÂÛÔÊéèàâûô' COLLATE UNICODE_CI_AI ,'true','false'),'true','''EEAAUOEEEAAUO'' = ''ÉÈÀÂÛÔÊéèàâûô'' COLLATE UNICODE_CI_AI' FROM RDB$DATABASE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
CASE   CONSTANT CONSTANT
====== ======== =======================================================
true   true     'eeaauoeeeaauo' = 'ÉÈÀÂÛÔÊéèàâûô' COLLATE UNICODE_CI_AI


CASE   CONSTANT CONSTANT
====== ======== =======================================================
true   true     'EEAAUOEEEAAUO' = 'ÉÈÀÂÛÔÊéèàâûô' COLLATE UNICODE_CI_AI

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

