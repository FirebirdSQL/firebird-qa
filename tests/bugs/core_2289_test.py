#coding:utf-8
#
# id:           bugs.core_2289
# title:        Wrong (primary) constraint name is reported for the foreign key violation during FK creation
# decription:   
# tracker_id:   CORE-2289
# min_versions: ['2.1.7']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "PACKET_DETAIL_FK" on table "PACKET_DETAIL"
    -Foreign key reference target does not exist
    -Problematic key value is ("PACKET_ID" = 753)
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

