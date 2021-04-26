#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_isql_17
# title:        gtcs-proc-isql-17
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_17.script
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
    create procedure insert_sno (sno varchar(5)) as
        declare c int;
    begin
        select count(*) from sp where sno = :sno into :c;
        if (c = 0 ) then
            insert into sp(sno) values(:sno);
    end
    ^
    set term ;^
    execute procedure insert_sno 'S10';
    select p.* from sp p;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SNO    PNO             QTY
    S1     P1              300
    S1     P3              400
    S2     P1              300
    S2     P2              400
    S4     P4              300
    S4     P5              400
    S10    <null>       <null>
  """

@pytest.mark.version('>=2.5')
def test_gtcs_proc_isql_17_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

