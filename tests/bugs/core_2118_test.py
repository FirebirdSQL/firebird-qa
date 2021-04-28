#coding:utf-8
#
# id:           bugs.core_2118
# title:        UPDATE OR INSERT with subquery used in the MATCHING part doesn't insert record
# decription:   
#                  14.08.2020:
#                  removed usage of generator because gen_id() result differs in FB 4.x vs previous versions since fixed core-6084.
#                  Use hard-coded value for ID that is written into table MACRO..
#                  Checked on:
#                       4.0.0.2151 SS: 1.749s.
#                       3.0.7.33348 SS: 0.897s.
#                       2.5.9.27150 SC: 0.378s.
#                 
# tracker_id:   CORE-2118
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', ''), ('[ \t]+', ' ')]

init_script_1 = """
    create table macro (
        id integer not null,
        t1 integer,
        code varchar(50)
    );

    create table param (
        id integer not null,
        p1 integer
    );

    commit;
    alter table macro add constraint pk_macro primary key (id);
    alter table param add constraint pk_param primary key (id);
    commit;
    alter table macro add constraint fk_macro_1 foreign key (t1) references param (id);
    commit;

    insert into param (id, p1) values (2, 11);
    commit;
  """

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    update or insert into macro (id, t1, code) values ( 1, (select id from param where p1 = 11), 'fsdfdsf') matching (t1);
    commit;
    set list on;
    select id, t1, code from macro;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    T1                              2
    CODE                            fsdfdsf
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

