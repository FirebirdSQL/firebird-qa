#coding:utf-8
#
# id:           bugs.core_1175
# title:        Error "Data type unknown" when any UDF argument is a built-in function containing a DSQL parameter reference
# decription:
#                   For FB 2.5 and 3.x - this test uses UDF from ib_udf.
#
#                   24.01.2019. Added separate code for running on FB 4.0+.
#                   UDF usage is deprecated in FB 4+, see: ".../doc/README.incompatibilities.3to4.txt".
#                   Functions div, frac, dow, sdow, getExactTimestampUTC and isLeapYear got safe replacement
#                   in UDR library "udf_compat", see it in folder: ../plugins/udr/
#
#                   Checked on:
#                       4.0.0.1340: OK, 2.594s.
#                       4.0.0.1378: OK, 5.579s.
#
#                   NOTE. Build 4.0.0.1172 (date: 25.08.2018) raises here:
#                       SQLCODE: -902... expression evaluation not supported...
#                       Invalid data type for division in dialect 3
#                       gdscode = 335544569.
#
# tracker_id:   CORE-1175
# min_versions: []
# versions:     4.0
# qmid:         bugs.core_1175

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """
    -- See declaration sample in plugins\\udr\\UdfBackwardCompatibility.sql:
    create function UDR40_frac (
        val double precision
    ) returns double precision
    external name 'udf_compat!UC_frac'
    engine udr;

    create function UDR40_div (
        n1 integer,
        n2 integer
    ) returns double precision
    external name 'udf_compat!UC_div'
    engine udr;

    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# \\
#  c = db_conn.cursor()
#  try:
#      c.prep( 'select 1 from rdb$database where UDR40_frac( ? ) != UDR40_div( ?, ?) / ? ' )
#      print ( 'Test PASSED!' )
#  except Exception,e:
#      print( 'Test FAILED!' )
#      print( e )
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    with  act_1.db.connect() as con:
        c = con.cursor()
        try:
            c.prepare('select 1 from rdb$database where UDR40_frac(?) != UDR40_div(?, ?) / ?')
        except:
            pytest.fail('Test FAILED')


