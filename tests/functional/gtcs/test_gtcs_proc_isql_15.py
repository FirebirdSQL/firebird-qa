#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_isql_15
# title:        gtcs-proc-isql-15
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_15.script
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
    create procedure proc_insert (a char(5), b char(20), c char(6), d smallint, e char(15)) as
    begin
    insert into p values (:a, :b, :c, :d, :e);
    end
    ^
    set term ;^
    select 'point-1' msg, p.* from p;
    execute procedure proc_insert 'P7', 'Widget', 'Pink', 23, 'Hoboken';
    select 'point-2' msg, p.* from p;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG     PNO    PNAME                COLOR        WEIGHT CITY
    point-1 P1     Nut                  Red              12 London
    point-1 P2     Bolt                 Green            17 Paris
    point-1 P3     Screw                Blue             17 Rome
    point-1 P4     Screw                Red              14 London
    point-1 P5     Cam                  Blue             12 Paris
    point-1 P6     Cog                  Red              19 London

    MSG     PNO    PNAME                COLOR        WEIGHT CITY
    point-2 P1     Nut                  Red              12 London
    point-2 P2     Bolt                 Green            17 Paris
    point-2 P3     Screw                Blue             17 Rome
    point-2 P4     Screw                Red              14 London
    point-2 P5     Cam                  Blue             12 Paris
    point-2 P6     Cog                  Red              19 London
    point-2 P7     Widget               Pink             23 Hoboken
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

