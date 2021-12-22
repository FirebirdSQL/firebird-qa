#coding:utf-8
#
# id:           bugs.core_5322
# title:        Error "no current record to fetch" if some record is to be deleted both by the statement itself and by some trigger fired during statement execution
# decription:   
#                  Reproduced bug on WI-V3.0.0.32483, WI-T4.0.0.258
#                  All fine on WI-V3.0.1.32596, WI-T4.0.0.366.
#                
# tracker_id:   CORE-5322
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table tdetl(id int);
    commit;

    recreate table tmain (
        id integer not null,
        some_data integer
    );

    recreate table tdetl (
        id integer not null,
        tmain_id integer,
        some_data integer,
        parent_id integer
    );
    commit;

    insert into tmain (id, some_data) values (1, 10);
    commit;

    insert into tdetl (id, tmain_id, some_data, parent_id) values (1, 1, 555, null);
    insert into tdetl (id, tmain_id, some_data, parent_id) values (2, 1, 222, 1);
    commit;

    alter table tmain add constraint pk_tmain primary key (id);
    alter table tdetl add constraint pk_tdetl primary key (id);
    alter table tdetl add constraint fk_tdetl_1 foreign key (tmain_id) references tmain (id) on delete cascade;
    alter table tdetl add constraint fk_tdetl_2 foreign key (parent_id) references tdetl (id) on delete cascade;
    commit;

    delete from tmain where (id = 1);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.1')
def test_1(act_1: Action):
    act_1.execute()

