#coding:utf-8
#
# id:           bugs.core_6108
# title:        Regression: FB3 throws "Datatypes are not comparable in expression" in procedure parameters
# decription:
#                   Confirmed bug on 4.0.0.1567; 3.0.5.33160.
#                   Works fine on 4.0.0.1573; 3.0.x is still affected
#
# tracker_id:   CORE-6108
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  proc_ddl='''
#      create or alter procedure test_proc ( a_dts timestamp) returns ( o_dts timestamp) as
#      begin
#          o_dts = a_dts;
#          suspend;
#      end
#  '''
#
#  db_conn.execute_immediate( proc_ddl )
#  db_conn.commit()
#
#  cur=db_conn.cursor()
#
#  sttm="select o_dts from test_proc('2019-'|| COALESCE( ?, 1) ||'-01' )"
#  cur.execute( sttm, ( 3, ) )
#  for r in cur:
#      print(r[0])
#  cur.close()
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    2019-03-01 00:00:00
"""

proc_ddl = """
    create or alter procedure test_proc ( a_dts timestamp) returns ( o_dts timestamp) as
    begin
        o_dts = a_dts;
        suspend;
    end
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action, capsys):
    with act_1.db.connect() as con:
        con.execute_immediate(proc_ddl)
        con.commit()
        c = con.cursor()
        for row in c.execute("select o_dts from test_proc('2019-'|| COALESCE( ?, 1) ||'-01' )", [3]):
            print(row[0])
    #
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout


