#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_isql_18
# title:        gtcs-proc-isql-18
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_18.script
#               	SQL script for creating test database ('gtcs_sp1.fbk') and fill it with some data:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROCS_QA_INIT_ISQL.script
#                   Checked on:
#                       4.0.0.1803 SS: 1.822s.
#                       3.0.6.33265 SS: 0.849s.
#                       2.5.9.27149 SC: 0.313s.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('={3,}', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(from_backup='gtcs_sp1.fbk', init=init_script_1)

test_script_1 = """
    set term ^;
    create procedure proc_select_insert as
    begin
        insert into sp(sno) select sno from s where sno not in (select sno from sp);
    end
    ^
    set term ;^
    select 'point-1' as msg, p.* from sp p;
    execute procedure proc_select_insert;
    select 'point-2' as msg, p.* from sp p;
    rollback;
    select 'point-3' as msg, p.* from sp p;
    execute procedure proc_select_insert;
    select 'point-4' as msg, p.* from sp p;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG     SNO    PNO             QTY
    point-1 S1     P1              300
    point-1 S1     P3              400
    point-1 S2     P1              300
    point-1 S2     P2              400
    point-1 S4     P4              300
    point-1 S4     P5              400

    MSG     SNO    PNO             QTY
    point-2 S1     P1              300
    point-2 S1     P3              400
    point-2 S2     P1              300
    point-2 S2     P2              400
    point-2 S4     P4              300
    point-2 S4     P5              400
    point-2 S3     <null>       <null>
    point-2 S5     <null>       <null>

    MSG     SNO    PNO             QTY
    point-3 S1     P1              300
    point-3 S1     P3              400
    point-3 S2     P1              300
    point-3 S2     P2              400
    point-3 S4     P4              300
    point-3 S4     P5              400

    MSG     SNO    PNO             QTY
    point-4 S1     P1              300
    point-4 S1     P3              400
    point-4 S2     P1              300
    point-4 S2     P2              400
    point-4 S4     P4              300
    point-4 S4     P5              400
    point-4 S3     <null>       <null>
    point-4 S5     <null>       <null>
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

