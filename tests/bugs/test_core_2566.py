#coding:utf-8
#
# id:           bugs.core_2566
# title:        internal error [335544384]
# decription:   
# tracker_id:   CORE-2566
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    create table tab_partner (
        id_partner integer not null,
        stav char(1) not null,
        id_bankucet integer
    );

    create table typ_stav (hodnota char(1) not null);

    create view x_partner (id_partner, stav) as
    select p.id_partner, p.stav
    from tab_partner p
    left join typ_stav tss on p.stav=tss.hodnota
    ;

    insert into tab_partner(id_partner, stav, id_bankucet) values(0, 'A', null);

    select *
    from x_partner;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID_PARTNER                      0
    STAV                            A
  """

@pytest.mark.version('>=2.5')
def test_core_2566_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

