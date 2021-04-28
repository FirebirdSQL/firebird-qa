#coding:utf-8
#
# id:           functional.intfunc.date.datediff_06
# title:        test de la fonction datediff pour avoir le resultat en jour
# decription:   Returns an exact numeric value representing the interval of time from the first date/time/timestamp value to the second one.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.intfunc.date.datediff_06

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select datediff(DAY,cast( '12/02/2008 13:33:33' as timestamp),cast( '12/02/2009 13:34:35' as timestamp)) from rdb$database;
select datediff(DAY FROM cast( '12/02/2008 13:33:33' as timestamp) TO cast( '12/02/2009 13:34:35' as timestamp)) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
             DATEDIFF
=====================
                  365


             DATEDIFF
=====================
                  365

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

