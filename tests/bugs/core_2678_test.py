#coding:utf-8

"""
ID:          issue-3081
ISSUE:       3081
TITLE:       Full outer join cannot use available indices (very slow execution)
DESCRIPTION:
JIRA:        CORE-2678
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table td_data1 (
      c1 varchar(20) character set win1251 not null collate win1251,
      c2 integer not null,
      c3 date not null,
      d1 float not null
    );
    create index idx_td_data1 on td_data1(c1,c2,c3);
    commit;

    create table td_data2 (
      c1 varchar(20) character set win1251 not null collate win1251,
      c2 integer not null,
      c3 date not null,
      d2 float not null
    );
    create index idx_td_data2 on td_data2(c1,c2,c3);
    commit;

    set planonly;
    select
        d1.c1, d2.c1,
        d1.c2, d2.c2,
        d1.c3, d2.c3,
        coalesce(sum(d1.d1), 0) t1,
        coalesce(sum(d2.d2), 0) t2
    from td_data1 d1
    full join td_data2 d2
        on
            d2.c1 = d1.c1
            and d2.c2 = d1.c2
            and d2.c3 = d1.c3
    group by
        d1.c1, d2.c1,
        d1.c2, d2.c2,
        d1.c3, d2.c3;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN SORT (JOIN (JOIN (D2 NATURAL, D1 INDEX (IDX_TD_DATA1)), JOIN (D1 NATURAL, D2 INDEX (IDX_TD_DATA2))))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

