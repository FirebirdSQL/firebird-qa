#coding:utf-8
#
# id:           bugs.core_3895
# title:        High memory usage when PSQL code SELECT's from stored procedure which modified some data
# decription:
#                  Test does <run_cnt> calls of selectable SP which performs DML inside itself.
#                  After every call we store value of db_info(fdb.isc_info_current_memory) as new element in list.
#                  After all calls finish we scan list for difference between adjacent elements which exceeds
#                  <max_mem_leak> threshold.
#                  Value of this threshold depends on FB engine version.
#
#                  On current FB versions memory usage is incremented (after every call of SP, w/o commit) by:
#                  1) ~  1800 bytes for 2.5.7
#                  2) ~ 14500 bytes for 3.0
#
#                  Confirmed excessive memory usage on WI-V2.5.2.26540 (requires additional ~100 Kb).
#
# tracker_id:   CORE-3895
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    create or alter procedure sp_main returns (id integer) as begin suspend; end
    ^
    create or alter procedure sp_select_and_insert (p_id integer) returns (id integer) as begin suspend; end
    ^
    commit
    ^
    recreate table test (id integer)
    ^

    create or alter procedure sp_select_and_insert (p_id integer) returns (id integer) as
    begin
      insert into test(id) values(:p_id);
      id = p_id;
      suspend;
    end
    ^

    create or alter procedure sp_main returns (id integer)
    as
      declare i int = 0;
    begin
      while (i < 1000) do begin
        select id from sp_select_and_insert(:i) into :id;
        i = i + 1;
      end
      suspend;
    end
    ^
    commit
    ^
    set term ;^
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import fdb
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  # Obtain engine version:
#  cur1=db_conn.cursor()
#  cur1.execute("select rdb$get_context('SYSTEM','ENGINE_VERSION') as engine_version from rdb$database")
#  for row in cur1:
#      engine = row[0]
#  cur1.close()
#
#  sql_check="select id from sp_main"
#  cur2=db_conn.cursor()
#
#  mem_usage=[]
#  run_cnt=20
#
#  for i in range(0, run_cnt):
#      cur2.execute(sql_check)
#      for r in cur2:
#          pass
#      mem_usage.append( db_conn.db_info(fdb.isc_info_current_memory) )
#  cur2.close()
#  db_conn.close()
#
#  max_mem_leak=4096 if engine.startswith('2.5') else 16384
#
#  for i in range(1, run_cnt):
#      m0=mem_usage[i-1]
#      m1=mem_usage[i]
#      if m1 - m0 >= max_mem_leak:
#          print('Unexpected memory leak: '+str(m1-m0)+' bytes, exceeds threshold = '+str(max_mem_leak) ) # 2.5.2: 108532 ... 108960; 2.5.7: 1192 ... 1680
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    run_cnt = 20
    with act_1.db.connect() as con:
        c = con.cursor()
        mem_usage = []
        for i in range(0, run_cnt):
            c.execute('select id from sp_main')
            c.fetchall()
            mem_usage.append(con.info.current_memory)
    max_mem_leak = 16384 # FB 3+
    print(mem_usage)
    for i in range(2, run_cnt):
        m0 = mem_usage[i-1]
        m1 = mem_usage[i]
        if m1 - m0 >= max_mem_leak:
            pytest.fail(f'Unexpected memory leak: {m1-m0} bytes, exceeds threshold = {max_mem_leak}')
