#coding:utf-8
#
# id:           bugs.core_1000
# title:        Incorrect results when left join on subquery with constant column
# decription:   
# tracker_id:   CORE-1000
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE A (
    ID INTEGER
);

CREATE TABLE B (
    ID INTEGER
);

insert into A (id) values (1);
insert into A (id) values (2);
insert into A (id) values (3);

insert into B (id) values (1);
insert into B (id) values (2);

commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select a.id, b.id, bexists
from a
  left join (select id, 1 bexists from b) b on (a.id=b.id);

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID           ID      BEXISTS
============ ============ ============
           1            1            1
           2            2            1
           3       <null>       <null>

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

