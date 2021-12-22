#coding:utf-8
#
# id:           bugs.core_5908
# title:        Enhance dynamic libraries loading related error messages
# decription:
#                  We intentionally try to load unit from non-existent UDR module with name "udrcpp_foo".
#                  Message 'module not found' issued BEFORE fix - without any detailization.
#                  Current output should contain phrase: 'UDR module not loaded'.
#                  Filtering is used for prevent output of localized message about missed UDR library.
#
#                  Checked on:
#                      3.0.4.33053: OK, 13.968s.
#                      4.0.0.1210: OK, 2.375s.
#                  Thanks to Alex for suggestion about test implementation.
#
# tracker_id:   CORE-5908
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
import re
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DatabaseError

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import re
#
#  udr_sp_ddl='''
#      create or alter procedure gen_foo2 (
#          start_n integer not null,
#          end_n integer not null
#      ) returns( n integer not null )
#          external name 'udrcpp_foo!gen_rows'
#          engine udr
#  '''
#
#  allowed_patterns = (
#       re.compile('\\.*module\\s+not\\s+(found|loaded)\\.*', re.IGNORECASE),
#  )
#
#  try:
#      db_conn.execute_immediate( udr_sp_ddl )
#      db_conn.commit() # --------------------- this will fail with message about missed UDR livrary file.
#  except Exception,e:
#      ##############################################################################
#      # We parse exception object and allow for output only such lines from it
#      # that relate to missed MODULE, and no other text (localization can be here!):
#      ##############################################################################
#      for i in e[0].split('\\n'):
#          match2some = filter( None, [ p.search(i) for p in allowed_patterns ] )
#          if match2some:
#              print( (' '.join(i.split()).upper()) )
#  finally:
#      db_conn.close()
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    UDR module not loaded
"""

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action, capsys):
    udr_ddl = """
    create or alter procedure gen_foo2 (
        start_n integer not null,
        end_n integer not null
    ) returns( n integer not null )
        external name 'udrcpp_foo!gen_rows'
        engine udr
"""
    pattern = re.compile('\\.*module\\s+not\\s+(found|loaded)\\.*', re.IGNORECASE)
    with act_1.db.connect() as con:
        try:
            con.execute_immediate(udr_ddl)
            con.commit()
        except DatabaseError as e:
            for line in str(e).splitlines():
                if pattern.search(line):
                    print(line)
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
