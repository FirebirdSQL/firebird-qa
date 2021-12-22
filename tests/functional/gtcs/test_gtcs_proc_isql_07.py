#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_isql_07
# title:        gtcs-proc-isql-07
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_07.script
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
    create procedure proc7 returns (a integer) as
    begin
        for
            select distinct max(qty)
            from sp
            where qty > 300
            into :a
        do
            suspend;
    end
    ^
    set term ;^

    execute procedure proc7;

    set count on;

    select 'point-1' msg, p.* from proc7 p;
    select 'point-2' msg, max(p.a) from proc7 p;
    select 'point-3' msg, p.a from proc7 p;
    select 'point-4' msg, p.* from proc7 p order by p.a;
    select 'point-5' msg, p.a, avg(p.a) from proc7 p group by p.a having avg(p.a) > 350;
    select 'point-6' msg, p.a, avg(p.a) from proc7 p group by p.a;
    select 'point-7' msg, p.a from proc7 p where p.a = (select avg(x.a) from proc7 x);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A
    400

    MSG                A
    point-1          400
    Records affected: 1

    MSG              MAX
    point-2          400
    Records affected: 1

    MSG                A
    point-3          400

    Records affected: 1

    MSG                A
    point-4          400
    Records affected: 1

    MSG                A                   AVG
    point-5          400                   400
    Records affected: 1

    MSG                A                   AVG
    point-6          400                   400
    Records affected: 1

    MSG                A
    point-7          400
    Records affected: 1
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

