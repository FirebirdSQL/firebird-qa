#coding:utf-8
#
# id:           bugs.core_5222
# title:        SELECT WITH LOCK may raise unexpected update conflict errors under concurrent load
# decription:
#                   Prototype: https://groups.yahoo.com/neo/groups/firebird-support/conversations/messages/128920
#                   Done with suggestions from dimitr, see letter 01-may-2016 09:15.
#                   Confirmed on WI-V3.0.0.32366, WI-V3.0.0.32483, 3.0.0.32501 (SS,SC,CS) - it was enough to
#                   async. start THREE child ISQLs sessions, one or two of them always raise exception after
#                   few seconds with text: 'deadlock / update conflicts' and could not finish its job.
#
#                   Checked on: WI-V3.0.0.32503, 3.0.1.32570, WI-T4.0.0.157 - works fine.
#                   Checked on 4.0.0.322 (Classic, SuperClassic, SuperServer) - works OK.
#
#                   12.08.2018 ::: NB :::
#                   It is unclear now how this test can be implemented on 4.0 after introduction of READ CONSISTENCY
#                   with default value ReadConsistency = 1. According to doc:
#                   ===
#                       If ReadConsistency set to 1 (by default) engine ignores
#                       [NO] RECORD VERSION flags and makes all read-committed
#                       transactions READ COMMITTED READ CONSISTENCY.
#                   ===
#
#                   Also, doc\\README.read_consistency.md  says that:
#                   "Old read-committed isolation modes (**RECORD VERSION** and **NO RECORD VERSION**) are still
#                   allowed but considered as legacy and not recommended to use."
#
#                   This mean that one can NOT to check issues of this ticket under 4.0 using default (and recommended)
#                   value of config parameter 'ReadConsistency'.
#                   For that reason it was decided to make new EMPTY section of test for 4.0.
#
# tracker_id:   CORE-5222
# min_versions: ['3.0.0']
# versions:     3.0, 4.0
# qmid:         None

from __future__ import annotations
from typing import List
import pytest
import subprocess
import time
import re
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_files, temp_file

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    create or alter procedure p_increment as begin end;
    commit;
    recreate table gen_tab(
        id bigint primary key
    );
    recreate table gen_log (
        id bigint primary key,
        id_new bigint not null,
        id_diff bigint not null
    );

    set term ^;
    alter procedure p_increment (a_iter_cnt int default 1000)
    returns (
        proc_start timestamp,
        selected_id bigint,
        proc_finish timestamp
    ) as
        declare i bigint;
        declare id_new bigint;
    begin
        i = 1;
        proc_start = 'now';
        while (i <= a_iter_cnt ) do
        begin
            in autonomous transaction do
            begin

                select id
                from gen_tab with lock -- this raised SQLSTATE = 40001 / -update conflicts with concurrent update
                into selected_id;
                i = i + 1;

                id_new = selected_id + 1;
                insert into gen_log(id, id_new, id_diff)
                            values( :selected_id, :id_new, :id_new - :selected_id);

                update gen_tab set id = :id_new
                where id = :selected_id;

            end
        end
        proc_finish = 'now';

        suspend; -- outputs row with three fields: 'PROC_START <timestamp>', 'SELECTED_ID <id>', 'PROC_FINISH <timestamp>'
    end ^
    set term ;^
    commit;

    insert into gen_tab (id) values (0);
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  from subprocess import Popen
#  import re
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#
#  f_run_sql=open( os.path.join(context['temp_directory'],'tmp_5222_run.sql'), 'w')
#  f_run_sql.write('''    --show version;
#      commit;
#      set list on;
#      set transaction read committed no record_version lock timeout 3;
#      select current_timestamp as before_proc
#      from rdb$database;
#
#      select * from p_increment(10);
#
#      select current_timestamp as after_proc
#      from rdb$database;
#  ''')
#  f_run_sql.close()
#
#  ##########################################################################################
#  #  Launching several concurrent child ISQL processes which perform script from `f_run_sql`
#  ##########################################################################################
#  planned_dml_attachments = 3
#
#  f_list = []
#  p_list = []
#
#
#  for i in range(0, planned_dml_attachments):
#      sqllog=open( os.path.join(context['temp_directory'],'tmp_dml_5222_'+str(i)+'.log'), 'w')
#      f_list.append(sqllog)
#
#  for i in range(len(f_list)):
#      p_isql=Popen( [ context['isql_path'] , dsn, "-i", f_run_sql.name ],
#                    stdout=f_list[i],
#                    stderr=subprocess.STDOUT
#                  )
#      p_list.append(p_isql)
#
#  time.sleep(7)
#
#  for i in range(len(f_list)):
#      f_list[i].close()
#
#  for i in range(len(p_list)):
#      p_list[i].terminate()
#
#  # 12.08.2016: added small delay because it's possible to get:
#  # WindowsError:
#  # 32
#  # The process cannot access the file because it is being used by another process
#
#  time.sleep(2)
#
#  ###########################
#  # CHECK RESULTS and CLEANUP
#  ###########################
#
#  # 1. Each log _should_ contain ONLY following lines:
#  #    BEFORE_PROC                     2016-05-03 09:27:57.6210
#  #    PROC_START                      2016-05-03 09:27:57.6210
#  #    SELECTED_ID                     1569
#  #    PROC_FINISH                     2016-05-03 09:28:04.0740
#  #    AFTER_PROC                      2016-05-03 09:28:04.0740
#  # 2. _NO_ log should contain 'SQLSTATE = 40001'
#
#  # Open every log and print 1st word from each line, ignoring values of timestamp and ID.
#  # Then close log and remove it:
#
#  pattern = re.compile("BEFORE_PROC*|PROC_START*|SELECTED_ID*|PROC_FINISH*|AFTER_PROC*")
#  for i in range(len(f_list)):
#      with open( f_list[i].name, 'r') as f:
#          for line in f:
#              if line.split():
#                  if pattern.match(line):
#                      print( 'EXPECTED, LOG #'+str(i)+': '+line.split()[0] )
#                  else:
#                      print( 'UNEXPECTED, LOG #'+str(i)+': '+ line )
#      f.close()
#      os.remove(f_list[i].name)
#
#  os.remove(f_run_sql.name)
#
#  #           Sample of WRONG result (got on 3.0.0.32483):
#  #           ===============
#  #             EXPECTED, LOG #0: BEFORE_PROC
#  #             EXPECTED, LOG #0: PROC_START
#  #             EXPECTED, LOG #0: SELECTED_ID
#  #             EXPECTED, LOG #0: PROC_FINISH
#  #             EXPECTED, LOG #0: AFTER_PROC
#  #             EXPECTED, LOG #1: BEFORE_PROC
#  #             EXPECTED, LOG #1: PROC_START
#  #             EXPECTED, LOG #1: SELECTED_ID
#  #             EXPECTED, LOG #1: PROC_FINISH
#  #             EXPECTED, LOG #1: AFTER_PROC
#  #             EXPECTED, LOG #2: BEFORE_PROC
#  #           - EXPECTED, LOG #2: PROC_START
#  #           - EXPECTED, LOG #2: SELECTED_ID
#  #           - EXPECTED, LOG #2: PROC_FINISH
#  #           + UNEXPECTED, LOG #2: Statement failed, SQLSTATE = 40001
#  #           + UNEXPECTED, LOG #2: deadlock
#  #           + UNEXPECTED, LOG #2: -update conflicts with concurrent update
#  #           + UNEXPECTED, LOG #2: -concurrent transaction number is 32
#  #           + UNEXPECTED, LOG #2: -At procedure 'P_INCREMENT' line: 17, col: 17
#  #           + UNEXPECTED, LOG #2: After line 6 in file C:\\MIX\\Firebird\\QA\\fbt-repo\\tmp\\tmp_5222_run.sql
#  #             EXPECTED, LOG #2: AFTER_PROC
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

test_script_1 = """
    commit;
    set list on;
    set transaction read committed no record_version lock timeout 3;
    select current_timestamp as before_proc
    from rdb$database;

    select * from p_increment(10);

    select current_timestamp as after_proc
    from rdb$database;
"""

expected_stdout_1 = """
    EXPECTED, LOG #0: BEFORE_PROC
    EXPECTED, LOG #0: PROC_START
    EXPECTED, LOG #0: SELECTED_ID
    EXPECTED, LOG #0: PROC_FINISH
    EXPECTED, LOG #0: AFTER_PROC

    EXPECTED, LOG #1: BEFORE_PROC
    EXPECTED, LOG #1: PROC_START
    EXPECTED, LOG #1: SELECTED_ID
    EXPECTED, LOG #1: PROC_FINISH
    EXPECTED, LOG #1: AFTER_PROC

    EXPECTED, LOG #2: BEFORE_PROC
    EXPECTED, LOG #2: PROC_START
    EXPECTED, LOG #2: SELECTED_ID
    EXPECTED, LOG #2: PROC_FINISH
    EXPECTED, LOG #2: AFTER_PROC
"""

PLANNED_DML_ATTACHMENTS = 3

run_sql = temp_file('core_5222_run.sql')
dml_logs_1 = temp_files([f'tmp_dml_5222_{i+1}' for i in range(PLANNED_DML_ATTACHMENTS)])

@pytest.mark.version('>=3.0,<4')
def test_1(act_1: Action, run_sql: Path, dml_logs_1: List[Path], capsys):
    pattern = re.compile("BEFORE_PROC*|PROC_START*|SELECTED_ID*|PROC_FINISH*|AFTER_PROC*")
    run_sql.write_text(test_script_1)
    # Launching several concurrent child ISQL processes which perform `run_sql` script
    f_logs = []
    p_dml = []
    try:
        for dml_log in dml_logs_1: # Contains PLANNED_DML_ATTACHMENTS items
            f = open(dml_log, mode='w')
            f_logs.append(f)
            p_dml.append(subprocess.Popen([act_1.vars['isql'],
                                           '-i', str(run_sql),
                                           '-user', act_1.db.user,
                                           '-password', act_1.db.password,
                                           act_1.db.dsn],
                                          stdout=f, stderr=subprocess.STDOUT))
        #
        time.sleep(PLANNED_DML_ATTACHMENTS * 5)
    finally:
        for f in f_logs:
            f.close()
        for p in p_dml:
            p.terminate()
    #
    # 1. Each log _should_ contain ONLY following lines:
    #    BEFORE_PROC                     2016-05-03 09:27:57.6210
    #    PROC_START                      2016-05-03 09:27:57.6210
    #    SELECTED_ID                     1569
    #    PROC_FINISH                     2016-05-03 09:28:04.0740
    #    AFTER_PROC                      2016-05-03 09:28:04.0740
    # 2. _NO_ log should contain 'SQLSTATE = 40001'
    #
    # Open every log and print 1st word from each line, ignoring values of timestamp and ID.
    i = 0
    for dml_log in dml_logs_1:
        for line in dml_log.read_text().splitlines():
            if line.split():
                if pattern.match(line):
                    print(f'EXPECTED, LOG #{i}: {line.split()[0]}')
                else:
                    print(f'UNEXPECTED, LOG #{i}: {line}')
        i += 1
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

# test_script_2
#---
#
#
#---
#act_2 = python_act('db_2', test_script_2, substitutions=substitutions_2)


@pytest.mark.version('>=4.0')
def test_2(db_2):
    pytest.skip("Requires changed firebird.conf [ReadConsistency=0]")


