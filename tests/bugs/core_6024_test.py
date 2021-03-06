#coding:utf-8
#
# id:           bugs.core_6024
# title:        FB3.0.4.33063 vs FB3.0.5.33100 manual plan cause "index cannot be used in the specified plan"
# decription:   
#                   Confirmed bug on 3.0.5.33152 (got "index PK_WPLATA cannot be used in the specified plan").
#                   On 3.0.5.33212 execution for expression WITHOUT explicit 'plan ...' clause will use: PLAN (W ORDER PK_WPLATA).
#                   On 3.0.5.33215 both plans are as expected.
#               
#                   ::: NB :::
#                   As of 20.12.2019, FB 4.0.0.1693 has the same problem and not yet fixed.
#                
# tracker_id:   CORE-6024
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table wplata
    (
        dyr_id smallint not null,
        okres_numer char(7) not null,
        insp_id smallint not null,
        konto_id smallint not null,
        wplata_data_wyciagu date not null,
        wplata_nr_wyciagu varchar(10) not null,
        wplata_nr_pozycji smallint not null,
        wplata_kontrahent_id integer,
        constraint pk_wplata primary key (dyr_id,insp_id,konto_id,wplata_data_wyciagu,wplata_nr_wyciagu,wplata_nr_pozycji)
    );

    create index ixa_wplata__kontrahent__pk on wplata (wplata_kontrahent_id,dyr_id);

    -----------------------------------------------------------------------------------------------------

    set plan on;

    select
        w.dyr_id
        , w.insp_id
        , w.konto_id
        , w.wplata_data_wyciagu
        , w.wplata_nr_wyciagu
        , w.wplata_nr_pozycji
    from wplata w
    where
        w.wplata_kontrahent_id in (1452)
        and w.dyr_id = 6
    order by
        w.dyr_id
        , w.insp_id
        , w.konto_id
        , w.wplata_data_wyciagu
        , w.wplata_nr_wyciagu
        , w.wplata_nr_pozycji
    ;


    select
        w.dyr_id
        , w.insp_id
        , w.konto_id
        , w.wplata_data_wyciagu
        , w.wplata_nr_wyciagu
        , w.wplata_nr_pozycji
    from wplata w
    where
        w.wplata_kontrahent_id in (1452)
        and w.dyr_id = 6
    plan(w order pk_wplata index(ixa_wplata__kontrahent__pk))
    order by
        w.dyr_id
        , w.insp_id
        , w.konto_id
        , w.wplata_data_wyciagu
        , w.wplata_nr_wyciagu
        , w.wplata_nr_pozycji
    ;


  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (W INDEX (IXA_WPLATA__KONTRAHENT__PK))
    PLAN (W ORDER PK_WPLATA INDEX (IXA_WPLATA__KONTRAHENT__PK))
  """

@pytest.mark.version('>=3.0.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

