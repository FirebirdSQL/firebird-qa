#coding:utf-8

"""
ID:          issue-6522
ISSUE:       6522
TITLE:       MERGE statement loses parameters in WHEN (NOT) MATCHED clause that will never be matched, crashes server in some situations
DESCRIPTION:
  Confirmed crash on WI-V3.0.5.33220, WI-T4.0.0.1871 - but only when run MERGE statements with parameters from Python. NO crash when run it from ISQL.
  No crash on 4.0.0.1881, but message "No SQLDA for input values provided" will raise for any number of input parameters: 2 or 3.
NOTES:
[14.12.2021] pcisar
  It's impossible to reimplement it in the same way with new driver.
  PROBLEM:
  Original test used two parameter values where 3 parameters are expected, but
  new driver does not even allow that as it checks number of values with number of
  parameters - returned by iMessageMetadata.get_count().
  ALSO, as new driver uses OO API, it does not use SQLDA structures at all.
JIRA:        CORE-6280
"""

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

init_script = """
    recreate table t(i int not null primary key, j int);
"""

db = db_factory(init=init_script)

act = python_act('db')

expected_stdout = """
    Error while executing SQL statement:
    - SQLCODE: -902
    - Dynamic SQL Error
    - SQLDA error
    - No SQLDA for input values provided
"""

@pytest.mark.skip("FIXME: see notes")
@pytest.mark.version('>=3.0.6')
def test_1(act: Action):
    with act.db.connect() as con:
        c = con.cursor()
        cmd = """
            merge into t
            using (select 1 x from rdb$database) on 1 = 1
            when matched then
                update set j = ?
            when matched and i = ? then
                delete
            when not matched then
                insert (i, j) values (1, ?)
        """
        # PROBLEM:
        # Original test used two parameter values where 3 parameters are expected, but
        # new driver does not even allow that as it checks number of values with number of
        # parameters - returned by iMessageMetadata.get_count().
        # ALSO, as new driver uses OO API, it does not use SQLDA structures at all.
        #with pytest.raises(DatabaseError):
            #c.execute(cmd, [1, 2])
        # Next passes ok on v4.0.0.2496, but does it really tests the original issue?
        c.execute(cmd, [1, 2, 3])

# test_script_1
#---
#
#  cur=db_conn.cursor()
#  stm='''
#      merge into t
#      using (select 1 x from rdb$database) on 1 = 1
#      when matched then
#          update set j = ?
#      when matched and i = ? then
#          delete
#      when not matched then
#          insert (i, j) values (1, ?)
#  '''
#
#  try:
#      cur.execute( stm ) (1,2,)
#      # cur.execute( stm ) (1,2,3,) -- also leads to "No SQLDA for input values provided"
#  except Exception as e:
#      print(e[0])
#  finally:
#      cur.close()
#      db_conn.close()
#
#
#---

