#coding:utf-8
#
# id:           bugs.core_2766
# title:        Error "page 0 is of wrong type (expected 6, found 1)" is thrown while accessing a non-corrupted table
# decription:   
# tracker_id:   CORE-2766
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t_master (id int not null, name varchar(64));
alter table t_master add constraint PK_master primary key (id);

create table t_detail (id_master int not null, name varchar(64));
alter table t_detail add constraint FK_detail foreign key (id_master) references t_master (id);

commit;

insert into t_master values (1, '1');
insert into t_detail values (1, 'a');
commit;
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """insert into t_master values (3, '2');
delete from t_master where id = 3;
commit;

drop table t_detail;
commit;

delete from t_master;
select count(*) from t_master;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                COUNT
=====================
                    0

"""

@pytest.mark.version('>=3.0')
def test_core_2766_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

