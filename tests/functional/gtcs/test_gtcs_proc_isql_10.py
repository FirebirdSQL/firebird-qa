#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_isql_10
# title:        gtcs-proc-isql-10
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_10.script
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
    create procedure proc10  returns( a varchar(20), b varchar(5), c integer) as
    begin
        for
            select pname, color, weight
            from p where color = 'Red'
            order by weight
            into :a,:b,:c
        do
            suspend;
    end
    ^
    set term ;^

    set count on;
    execute procedure proc10 ;

    select 'point-1' msg, p.* from proc10 p;
    select 'point-2' msg, max(p.a) from proc10 p;
    select 'point-3' msg, p.c from proc10 p;
    select 'point-4' msg, p.a, p.c from proc10 p order by p.a;
    select 'point-5' msg, p.a, avg(p.c) from proc10 p group by p.a having avg(p.c) > 15;
    select 'point-6' msg, p.a, avg(p.c) from proc10 p group by p.a;
    select 'point-7' msg, p.a, p.c from proc10 p where p.c > (select avg(x.c) from proc10 x);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                    B                 C
    Nut                  Red              12

    MSG     A                    B                 C
    point-1 Nut                  Red              12
    point-1 Screw                Red              14
    point-1 Cog                  Red              19
    Records affected: 3

    MSG     MAX
    point-2 Screw
    Records affected: 1

    MSG                C
    point-3           12
    point-3           14
    point-3           19
    Records affected: 3

    MSG     A                               C
    point-4 Cog                            19
    point-4 Nut                            12
    point-4 Screw                          14
    Records affected: 3

    MSG     A                                      AVG
    point-5 Cog                                     19
    Records affected: 1

    MSG     A                                      AVG
    point-6 Cog                                     19
    point-6 Nut                                     12
    point-6 Screw                                   14
    Records affected: 3

    MSG     A                               C
    point-7 Cog                            19
    Records affected: 1
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

