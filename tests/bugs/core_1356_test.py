#coding:utf-8
#
# id:           bugs.core_1356
# title:        TYPE OF COLUMN in PSQL
# decription:   
# tracker_id:   CORE-1356
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter procedure sp_ins_person as begin end;
    commit;
    recreate table person (
      id integer,
      name varchar(40)
    );
    commit;

    set term ^;
    create or alter procedure sp_ins_person (
      id type of column person.id,
      name type of column person.name
    ) as
        declare variable new_id type of column person.id;
    begin
      insert into person (id, name) values (:id, :name) returning id into :new_id;
    end^
    set term ;^
    commit;
    --show procedure sp_ins_person;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.execute()

