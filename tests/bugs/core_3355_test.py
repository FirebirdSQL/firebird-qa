#coding:utf-8
#
# id:           bugs.core_3355
# title:        Wrong comparsion of DATE and TIMESTAMP if index is used
# decription:   
# tracker_id:   CORE-3355
# min_versions: ['2.1.5']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table tdate (id integer not null primary key, val date);
create index tdateix1 on tdate (val);
commit;
insert into tdate values (0, '1997-12-31');
insert into tdate values (1, '1998-01-01');
insert into tdate values (2, '1998-01-02');
insert into tdate values (3, '1998-01-03');
insert into tdate values (4, '1998-01-04');
insert into tdate values (5, '1998-01-05');
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select count(*) from tdate where val >= timestamp'1998-01-04 12:00:00.0000';
select count(*) from tdate where val < timestamp'1998-01-04 12:00:00.0000';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                COUNT
=====================
                    1


                COUNT
=====================
                    5

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

