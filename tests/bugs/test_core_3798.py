#coding:utf-8
#
# id:           bugs.core_3798
# title:        fb server die when carry out the LEFT + INNER JOIN
# decription:   
# tracker_id:   CORE-3798
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table table1 (
        id integer not null,
        name varchar(30),
        id_breed integer
    );
    alter table table1 add constraint pk_table1 primary key (id);
    
    recreate table table2 (
        id integer not null,
        id_table1 integer
    );
    alter table table2 add constraint pk_table2 primary key (id);
    
    recreate table table3 (
        id integer not null,
        id_breed integer
    );
    alter table table3 add constraint pk_table3 primary key (id);
    commit;
    
    select table2.id
    from table2
        left join table1 on table1.id = table2.id_table1
        inner join table3 on table1.id_breed = table3.id_breed
    where table1.id = 1
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_3798_1(act_1: Action):
    act_1.execute()

