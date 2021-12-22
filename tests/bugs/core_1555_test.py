#coding:utf-8
#
# id:           bugs.core_1555
# title:        'select ...from...where...not in (select...from...)' no results
# decription:   
# tracker_id:   
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         bugs.core_1555

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^ ;
    create or alter procedure tst1 returns (boxes integer) as
    begin
      boxes=1;
      suspend;
      boxes=2;
      suspend;
    end
    ^
    set term ;^
    commit;
    
    recreate table frrates1 (
      frrates1 integer not null,
      boxes integer,
      primary key(frrates1)
    );
    commit;
    
    create index idx_frrates1_boxes on frrates1 (boxes);
    commit;
    
    recreate table schedpkgs1 (
      schedpkgs1 integer not null,
      schedule integer,
      frrates1 integer,
      primary key (schedpkgs1)
    );
    commit;
    
    create index idx_schedpkgs1_schedule on schedpkgs1 (schedule);
    commit;
    
    
    insert into frrates1 (frrates1, boxes) values (11, 1);
    insert into frrates1 (frrates1, boxes) values (12, 2);
    commit;
    
    insert into schedpkgs1 (schedpkgs1, schedule, frrates1) values(21, 16651, 11);
    insert into schedpkgs1 (schedpkgs1, schedule, frrates1) values(22, 16651, null);
    commit;

    ---------------------------

    set list on;

    select fr.boxes
      from schedpkgs1 sp
      join frrates1 fr on fr.frrates1=sp.frrates1
      where sp.schedule = 16651;
    
   
    select boxes
      from tst1
      where boxes not in (select fr.boxes
                               from schedpkgs1 sp
                               join frrates1 fr on fr.frrates1=sp.frrates1
                               where sp.schedule = 16651);
    
   
    select boxes
      from tst1
      where boxes not in (select fr.boxes
                               from schedpkgs1 sp
                               join frrates1 fr on fr.frrates1=sp.frrates1
                               where sp.schedule = 16651 and fr.boxes>0);
    
    
    select f2.boxes
      from frrates1 f2
      where f2.boxes not in (select fr.boxes
                                  from schedpkgs1 sp
                                  join frrates1 fr on fr.frrates1=sp.frrates1
                                  where sp.schedule = 16651);
    
    select f2.boxes
      from frrates1 f2
      where f2.boxes not in (select fr.boxes
                                  from schedpkgs1 sp
                                  join frrates1 fr on fr.frrates1=sp.frrates1
                                  where sp.schedule = 16651 and fr.boxes>0);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    BOXES                           1
    BOXES                           2
    BOXES                           2
    BOXES                           2
    BOXES                           2
"""

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

