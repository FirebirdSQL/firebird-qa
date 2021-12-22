#coding:utf-8
#
# id:           functional.tabloid.gtcs_proc_isql_14
# title:        gtcs-proc-isql-14
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_14.script
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

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(from_backup='gtcs_sp1.fbk', init=init_script_1)

test_script_1 = """
    set bail on;
    set term ^;
    create procedure proc14 returns (a varchar(20), b integer) as
    begin
       for
           select pname,weight
           from p
           where weight < (select avg(weight) from p)
           into :a, :b
       do
           suspend;
    end
    ^
    set term ;^

    execute procedure proc14 ;

    select 'point-1' msg, p.* from proc14 p;
    select 'point-2' msg, max(p.b) from proc14 p;
    select 'point-3' msg, p.b from proc14 p;
    select 'point-4' msg, p.a, p.b from proc14 p order by p.a;
    select 'point-5' msg, p.a, avg(p.b) from proc14 p group by p.a having avg(p.b) > 10;
    select 'point-6' msg, p.a, avg(p.b) from proc14 p group by p.a;
    select 'point-7' msg, p.a, p.b from proc14 p where p.b > (select avg(x.b) from proc14 x);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               B
    Nut                            12


    MSG     A                               B
    point-1 Nut                            12
    point-1 Screw                          14
    point-1 Cam                            12

    MSG              MAX
    point-2           14

    MSG                B
    point-3           12
    point-3           14
    point-3           12

    MSG     A                               B
    point-4 Cam                            12
    point-4 Nut                            12
    point-4 Screw                          14

    MSG     A                                      AVG
    point-5 Cam                                     12
    point-5 Nut                                     12
    point-5 Screw                                   14

    MSG     A                                      AVG
    point-6 Cam                                     12
    point-6 Nut                                     12
    point-6 Screw                                   14

    MSG     A                               B
    point-7 Screw                          14
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

