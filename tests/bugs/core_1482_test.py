#coding:utf-8

"""
ID:          issue-1898
ISSUE:       1898
TITLE:       Make optimizer to consider ORDER BY optimization when making decision about join order
DESCRIPTION:
JIRA:        CORE-1482
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table tcolor(id int , name varchar(20) );
    recreate table thorses(id int, color_id int, name varchar(20));
    commit;

    set term ^;
    execute block as
      declare i int;
      declare n_main int = 50;
      declare ratio int = 1000;
    begin
      i = 0;
      while (i < n_main) do
      begin
        i = i + 1;
        insert into tcolor(id, name)
        values (:i, 'color #' || :i);
      end
      i = 0;
      while (i < n_main * ratio) do
      begin
        i = i + 1;
        insert into thorses(id, color_id, name)
        values (:i, mod(:i, :n_main)+1,  'horse #' || :i);
      end
    end
    ^
    set term ;^
    commit;

    create index tcolor_id on tcolor(id);
    create index thorses_color_id on thorses(color_id);
    -- this index was forgotten in previous revisions:
    create index thorses_id on thorses(id);
    commit;

    set list on;
    select (select count(*) from tcolor) colors_cnt, (select count(*) from thorses) horses_cnt
    from rdb$database;
    set planonly;
    -- in 2.1 and 2.5: PLAN SORT (JOIN (M NATURAL, D INDEX (THORSES_COLOR_ID))) -- doesn`t see 'rows 1'
    -- in 3.0 plan should CHANGE and take in account 'rows N' limit:
    select * from tcolor m join thorses d on m.id = d.color_id order by d.id rows 1;
"""

act = isql_act('db', test_script)

expected_stdout = """
    COLORS_CNT                      50
    HORSES_CNT                      50000

    PLAN JOIN (D ORDER THORSES_ID, M INDEX (TCOLOR_ID))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

