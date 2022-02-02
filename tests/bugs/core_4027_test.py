#coding:utf-8

"""
ID:          issue-4357
ISSUE:       4357
TITLE:       Creating table with computed fields containing "SELECT FIRST" produces corrupted result
DESCRIPTION: Broken output in ISQL command SHOW TABLE <T> for computed-by field(s).
JIRA:        CORE-4027
FBTEST:      bugs.core_4027
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- NB: fixed only in 3.0 (checked 30.03.2015)
    recreate table test (id int);
    commit;

    recreate table contragents (
        agent_id   int not null
        ,agent_name varchar(25) not null
    );
    commit;

    recreate table turnovers(
        po_number  char(8) not null
        ,agent_id   int not null
        ,order_date timestamp default 'now' not null
    );
    commit;

    recreate table test (
        agent_id integer not null,
        first_po_number computed by (
            (
                select first 1 t.po_number
                from turnovers t
                where t.agent_id=test.agent_id
                order by t.order_date
            )
        ),
        agent_name computed by (
            (
                select agent_name
                from contragents a
                where a.agent_id = test.agent_id
            )
        )
    );
    commit;
    show table test;
"""

act = isql_act('db', test_script)

expected_stdout = """
    AGENT_ID                        INTEGER Not Null
    FIRST_PO_NUMBER                 Computed by: (
                (
                    select first 1 t.po_number
                    from turnovers t
                    where t.agent_id=test.agent_id
                    order by t.order_date
                )
            )
    AGENT_NAME                      Computed by: (
                (
                    select agent_name
                    from contragents a
                    where a.agent_id = test.agent_id
                )
            )
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

