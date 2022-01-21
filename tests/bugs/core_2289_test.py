#coding:utf-8

"""
ID:          issue-2714
ISSUE:       2714
TITLE:       Wrong (primary) constraint name is reported for the foreign key violation during FK creation
DESCRIPTION:
JIRA:        CORE-2289
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table packet_detail(id int, packet_id int);
    recreate table packet(id int, constraint packet_pk primary key(id) using index packet_idx);
    commit;
    insert into packet_detail(id, packet_id) values(1, 753);
    commit;

    alter table packet_detail
    add constraint packet_detail_fk
    foreign key (packet_id)
    references packet(id)
    using index packet_detail_idx
    ;
    commit;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "PACKET_DETAIL_FK" on table "PACKET_DETAIL"
    -Foreign key reference target does not exist
    -Problematic key value is ("PACKET_ID" = 753)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

