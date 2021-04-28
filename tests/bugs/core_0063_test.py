#coding:utf-8
#
# id:           bugs.core_0063
# title:        Sequence of commands crash FB server
# decription:   
# tracker_id:   CORE-0063
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='WIN1252', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;

    create domain d_descricao_30000_nn as varchar(30000) not null collate win_ptbr;
    create table movimento( complemento d_descricao_30000_nn );

    insert into movimento values ('');
    insert into movimento values ('1234567890');
    insert into movimento values ('');

    create domain d_text_blob as blob sub_type text collate win_ptbr;

    alter table movimento add complemento2 d_text_blob;

    update movimento set complemento2 = complemento;

    alter table movimento drop complemento, add complemento d_text_blob;

    drop domain d_descricao_30000_nn;

    update movimento set complemento = complemento2;
    set list on;
    select 'OK' as result from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT                          OK
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

