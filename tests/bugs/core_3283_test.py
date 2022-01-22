#coding:utf-8

"""
ID:          issue-3651
ISSUE:       3651
TITLE:       BAD PLAN with using LEFT OUTER JOIN in SUBSELECT
DESCRIPTION:
JIRA:        CORE-3283
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table ttt (
        id int
        ,constraint ttt_pk primary key (id) using index ttt_id
    );

    insert into ttt (id) values (0);
    insert into ttt (id) values (1);
    insert into ttt (id) values (2);
    insert into ttt (id) values (3);
    insert into ttt (id) values (4);
    insert into ttt (id) values (5);
    commit;

    set planonly;
    select t1.id from ttt t1
    where t1.id =
    (select t3.id
       from ttt t2
       left join ttt t3 on t3.id > t2.id
      where t2.id = 3
      order by t3.id
       rows 1
    );

"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN SORT (JOIN (T2 INDEX (TTT_ID), T3 INDEX (TTT_ID)))
    PLAN (T1 INDEX (TTT_ID))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

