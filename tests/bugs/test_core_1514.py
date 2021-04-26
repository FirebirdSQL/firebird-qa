#coding:utf-8
#
# id:           bugs.core_1514
# title:        Many new 2.1 built in functions have incorrect NULL semantics
# decription:   
# tracker_id:   CORE-1514
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1514

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT ABS(null) from rdb$database;
SELECT ACOS(null) from rdb$database;
SELECT ASCII_VAL(null) from rdb$database;
SELECT ASIN(null) from rdb$database;
SELECT ATAN(null) from rdb$database;
SELECT ATAN2(null,null) from rdb$database;
SELECT BIN_AND(null,null) from rdb$database;
SELECT BIN_OR(null,null) from rdb$database;
SELECT BIN_XOR(null,null) from rdb$database;
SELECT COS(null) from rdb$database;
SELECT COSH(null) from rdb$database;
SELECT COT(null) from rdb$database;
SELECT dateadd(year, null, current_date) from rdb$database;
SELECT FLOOR(null) from rdb$database;
SELECT LN(null) from rdb$database;
SELECT LOG(null,null) from rdb$database;
SELECT LOG10(null) from rdb$database;
SELECT MOD(null,null) from rdb$database;
SELECT SIGN(null) from rdb$database;
SELECT SIN(null) from rdb$database;
SELECT SINH(null) from rdb$database;
SELECT SQRT(null) from rdb$database;
SELECT TAN(null) from rdb$database;
SELECT TANH(null) from rdb$database;
select trunc(1, cast(null as integer)) from rdb$database;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
         ABS
============
      <null>


                   ACOS
=======================
                 <null>


ASCII_VAL
=========
   <null>


                   ASIN
=======================
                 <null>


                   ATAN
=======================
                 <null>


                  ATAN2
=======================
                 <null>


     BIN_AND
============
      <null>


      BIN_OR
============
      <null>


     BIN_XOR
============
      <null>


                    COS
=======================
                 <null>


                   COSH
=======================
                 <null>


                    COT
=======================
                 <null>


    DATEADD
===========
     <null>


       FLOOR
============
      <null>


                     LN
=======================
                 <null>


                    LOG
=======================
                 <null>


                  LOG10
=======================
                 <null>


         MOD
============
      <null>


   SIGN
=======
 <null>


                    SIN
=======================
                 <null>


                   SINH
=======================
                 <null>


                   SQRT
=======================
                 <null>


                    TAN
=======================
                 <null>


                   TANH
=======================
                 <null>


       TRUNC
============
      <null>

"""

@pytest.mark.version('>=2.5')
def test_core_1514_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

