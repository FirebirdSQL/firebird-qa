#coding:utf-8

"""
ID:          issue-1602
ISSUE:       1602
TITLE:       Wrong result when use "where <field_C> STARTING WITH <:value> ORDER BY <field_N>"
  and field_C is leading part of compound index key: { field_C, field_N }
DESCRIPTION:
JIRA:        CORE-4665
FBTEST:      bugs.core_4665
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test (id int, unit varchar(10), y int, z int);
    commit;
    delete from test;

    insert into test( id, unit, y, z) values (1, 'foo', 9999, 23636);
    insert into test( id, unit, y, z) values (2, 'foo', 8888, 22520);
    insert into test( id, unit, y, z) values (3, 'foo', 5555, 21822);
    insert into test( id, unit, y, z) values (4, 'foo', 3333, 17682);

    insert into test( id, unit, y, z) values (5, 'fooo', 1111, 22);
    insert into test( id, unit, y, z) values (6, 'fooo', 111, 222);
    insert into test( id, unit, y, z) values (7, 'fooo', 11, 2222);
    insert into test( id, unit, y, z) values (8, 'fooo', 1, 22222);
    commit;

    create index test_unit_y_asc on test( unit, y );
    commit;

    set plan on;

    select id, t.unit, t.y, t.z
    from test t
    where t.unit||'' starting with 'foo'
    order by t.y||'';

    select id, t.unit, t.y, t.z
    from test t
    where t.unit starting with 'foo'
    order by t.y;
    set plan off;

    commit;
    drop index test_unit_y_asc;
    commit;

    create descending index test_unit_y_desc on test( unit, y);
    commit;

    set plan on;
    select id, t.unit, t.y, t.z
    from test t
    where t.unit starting with 'foo'
    order by t.y;
    set plan off;
"""

act = isql_act('db', test_script, substitutions=[('=.*', '')])

expected_stdout = """
    PLAN SORT (T NATURAL)

              ID UNIT                  Y            Z
    ============ ========== ============ ============
               8 fooo                  1        22222
               7 fooo                 11         2222
               6 fooo                111          222
               5 fooo               1111           22
               4 foo                3333        17682
               3 foo                5555        21822
               2 foo                8888        22520
               1 foo                9999        23636


    PLAN SORT (T INDEX (TEST_UNIT_Y_ASC))

              ID UNIT                  Y            Z
    ============ ========== ============ ============
               8 fooo                  1        22222
               7 fooo                 11         2222
               6 fooo                111          222
               5 fooo               1111           22
               4 foo                3333        17682
               3 foo                5555        21822
               2 foo                8888        22520
               1 foo                9999        23636


    PLAN SORT (T INDEX (TEST_UNIT_Y_DESC))

              ID UNIT                  Y            Z
    ============ ========== ============ ============
               8 fooo                  1        22222
               7 fooo                 11         2222
               6 fooo                111          222
               5 fooo               1111           22
               4 foo                3333        17682
               3 foo                5555        21822
               2 foo                8888        22520
               1 foo                9999        23636
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

