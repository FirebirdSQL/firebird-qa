#coding:utf-8
#
# id:           bugs.core_1795
# title:        Server crashes on SQL script
# decription:   
# tracker_id:   CORE-1795
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table colors (
      colorid integer not null,
      colorname varchar(20)
    );

    create table flowers (
      flowerid integer not null,
      flowername varchar(30),
      colorid integer
    );

    commit;

    insert into colors (colorid, colorname) values (0, 'not defined');
    insert into colors (colorid, colorname) values (1, 'red');
    insert into colors (colorid, colorname) values (2, 'white');
    insert into colors (colorid, colorname) values (3, 'blue');
    insert into colors (colorid, colorname) values (4, 'yellow');
    insert into colors (colorid, colorname) values (5, 'black');
    insert into colors (colorid, colorname) values (6, 'purple');

    insert into flowers (flowerid, flowername, colorid) values (1, 'red rose', 1);
    insert into flowers (flowerid, flowername, colorid) values (2, 'white rose', 2);
    insert into flowers (flowerid, flowername, colorid) values (3, 'blue rose', 3);
    insert into flowers (flowerid, flowername, colorid) values (4, 'yellow rose', 4);
    insert into flowers (flowerid, flowername, colorid) values (5, 'black rose', 5);
    insert into flowers (flowerid, flowername, colorid) values (6, 'red tulip', 1);
    insert into flowers (flowerid, flowername, colorid) values (7, 'white tulip', 2);
    insert into flowers (flowerid, flowername, colorid) values (8, 'yellow tulip', 4);
    insert into flowers (flowerid, flowername, colorid) values (9, 'blue gerbera', 3);
    insert into flowers (flowerid, flowername, colorid) values (10, 'purple gerbera', 6);

    commit;

    -- normally these indexes are created by the primary/foreign keys,
    -- but we don't want to rely on them for this test
    create unique asc index pk_colors on colors (colorid);
    create unique asc index pk_flowers on flowers (flowerid);
    create asc index fk_flowers_colors on flowers (colorid);
    create asc index i_colors_colorname on colors (colorname);
    commit;

    set list on;
    -- disable output of PLAN, it differ in 3.0 vs rest: set plan on;
    select
      f.colorid,
      c.colorname,
      count(*)
    from
      colors c
      left join flowers f on (f.colorid = c.colorid)
    group by
      f.colorid, c.colorname
    having
      c.colorname starting with 'b';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COLORID                         3
    COLORNAME                       blue
    COUNT                           2
    
    COLORID                         5
    COLORNAME                       black
    COUNT                           1
  """

@pytest.mark.version('>=2.1.7')
def test_core_1795_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

