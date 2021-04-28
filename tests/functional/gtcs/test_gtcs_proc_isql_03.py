#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_isql_03
# title:        gtcs-proc-isql-03
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_03.script
#               	SQL script for creating test database ('gtcs_sp1.fbk') and fill it with some data:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROCS_QA_INIT_ISQL.script
#                   Checked on: 4.0.0.1803 SS; 3.0.6.33265 SS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(from_backup='gtcs_sp1.fbk', init=init_script_1)

test_script_1 = """
    set bail on;
    set term ^;
    create procedure proc3  returns (a varchar(5), c integer) as
    begin
       for
           select pno, qty
           from sp
           where qty > 300 and pno = 'P5'
           into :a,  :c
       do
           suspend;
    end
    ^
    set term ;^

    execute procedure proc3; 

    set count on;

    select 'point-1' msg, p.* from proc3 p;
    select 'point-2' msg, max(p.a) from proc3 p;
    select 'point-3' msg, p.c from proc3 p;
    select 'point-4' msg, p.* from proc3 p order by p.a;
    select 'point-5' msg, p.a, avg(p.c) from proc3 p group by p.a having avg(p.c) > 350;
    select 'point-6' msg, p.a, avg(p.c) from proc3 p group by p.a;
    select 'point-7' msg, p.a, p.c from proc3 p where p.c = (select avg(x.c) from proc3 x);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                 C
    P5              400

    MSG     A                 C
    point-1 P5              400
    Records affected: 1

    MSG     MAX
    point-2 P5
    Records affected: 1

    MSG                C
    point-3          400
    Records affected: 1

    MSG     A                 C
    point-4 P5              400
    Records affected: 1

    MSG     A                        AVG
    point-5 P5                       400
    Records affected: 1

    MSG     A                        AVG
    point-6 P5                       400
    Records affected: 1

    MSG     A                 C
    point-7 P5              400
    Records affected: 1
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

