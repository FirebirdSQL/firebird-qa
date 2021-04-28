#coding:utf-8
#
# id:           bugs.core_0952
# title:        AV when blob is used in expression index
# decription:   
# tracker_id:   CORE-952
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_952

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """create table T (
     ID integer not null,
     N1 blob sub_type 1 segment size 80,
     N2 varchar(10)
);
commit;

insert into T (ID, N1, N2) values (1, 'www', 'qwer');
commit;

alter table T add constraint PK_T primary key (ID);
create index T_IDX on T computed by (cast(substring(N1 from 1 for 100) as varchar(100)));
commit;

update T set T.N2 = 'asdf' where T.ID = 1;
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT ID,N2 FROM T;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID N2
============ ==========
           1 asdf

"""

@pytest.mark.version('>=2.0.1')
def test_core_0952_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

