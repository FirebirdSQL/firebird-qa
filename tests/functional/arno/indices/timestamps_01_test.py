#coding:utf-8
#
# id:           functional.arno.indices.timestamps_01
# title:        TIMESTAMP in index with values below julian date
# decription:   Datetime values below the julian date (firebird base date '1858-11-17') should be stored in correct order.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.indexes.timestamps_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """
    create table era (
      begindatetime timestamp not null,
      enddatetime timestamp not null
    );
    commit;
    
    insert into era (begindatetime, enddatetime) values ('1500-01-01', '1550-12-31');
    insert into era (begindatetime, enddatetime) values ('1858-11-17', '1858-11-17');
    insert into era (begindatetime, enddatetime) values ('1858-11-15 18:00', '1858-11-15 20:00');
    insert into era (begindatetime, enddatetime) values ('1858-11-16 12:00', '1858-11-16 13:00');
    insert into era (begindatetime, enddatetime) values ('1858-11-18 16:00', '1858-11-18 17:00');
    insert into era (begindatetime, enddatetime) values ('2004-04-08 02:00', '2004-04-08 02:09');
    commit;
    
    create unique asc index pk_begindatetime on era (begindatetime);
    create unique asc index pk_enddatetime on era (enddatetime);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Queries with RANGE index scan now have in the plan only "ORDER"
    -- clause (index navigation) without bitmap building.
    -- See: http://tracker.firebirdsql.org/browse/CORE-1550
    -- ("the same index should never appear in both ORDER and INDEX parts of the same plan item")
    set plan on;
    select
      e.begindatetime,
      e.enddatetime
    from
      era e
    where
      e.begindatetime >= '1700-01-01'
    order by
      begindatetime asc;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (E ORDER PK_BEGINDATETIME)
                BEGINDATETIME               ENDDATETIME
    ========================= =========================
    1858-11-15 18:00:00.0000  1858-11-15 20:00:00.0000
    1858-11-16 12:00:00.0000  1858-11-16 13:00:00.0000
    1858-11-17 00:00:00.0000  1858-11-17 00:00:00.0000
    1858-11-18 16:00:00.0000  1858-11-18 17:00:00.0000
    2004-04-08 02:00:00.0000  2004-04-08 02:09:00.0000
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

