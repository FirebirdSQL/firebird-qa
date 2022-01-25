#coding:utf-8
#
# id:           bugs.gh_6740
# title:        Allow parenthesized query expression for standard-compliance
# decription:
#                   https://github.com/FirebirdSQL/firebird/issues/6740
#
#                   NOTE. Queries which do not use `WITH` clause now can be enclosed in parenthesis,
#                   but this leads to reduced number of max parts of UNIONed query, from 255 to 128.
#
#                   Checked on 5.0.0.88.
#
# tracker_id:
# min_versions: ['5.0']
# versions:     5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  # NB! Max limit of unioned-parts is 128 rather than 255!
#  ########################
#  NUM_OF_UNIONED_PARTS=128
#  ########################
#
#  unioned_query = '('
#  for i in range(0,NUM_OF_UNIONED_PARTS):
#    unioned_query = ''.join( (unioned_query, 'select %d ' % (i+1) + ('as i ' if i==0 else '') + 'from rdb$database') )
#    if i < NUM_OF_UNIONED_PARTS-1:
#        unioned_query = ''.join( (unioned_query, ' union all (') )
#
#  unioned_query = ''.join( (unioned_query, ')' * NUM_OF_UNIONED_PARTS) )
#  unioned_query += ';'
#
#  #print(unioned_query)
#
#  cur = db_conn.cursor()
#  cur.execute(unioned_query)
#  total = 0
#  for r in cur:
#      total += r[0]
#  cur.close()
#  print(total)
#---
act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    8256
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=5.0')
def test_1(act_1: Action):
    pytest.fail("Not IMPLEMENTED")
