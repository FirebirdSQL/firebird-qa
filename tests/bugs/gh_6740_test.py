#coding:utf-8

"""
ID:          issue-6740
ISSUE:       6740
TITLE:       Allow parenthesized query expression for standard-compliance
DESCRIPTION:
NOTES:
  Queries which do not use `WITH` clause now can be enclosed in parenthesis,
  but this leads to reduced number of max parts of UNIONed query, from 255 to 128.
JIRA:        CORE-6511
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    8256
"""

@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=5.0')
def test_1(act: Action):
    pytest.fail("Not IMPLEMENTED")

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
