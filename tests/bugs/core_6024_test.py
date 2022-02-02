#coding:utf-8

"""
ID:          issue-6274
ISSUE:       6274
TITLE:       FB3.0.4.33063 vs FB3.0.5.33100 manual plan cause "index cannot be used in the specified plan"
DESCRIPTION:
JIRA:        CORE-6024
FBTEST:      bugs.core_6024
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    PLAN SORT (W INDEX (IXA_WPLATA__KONTRAHENT__PK))
    PLAN (W ORDER PK_WPLATA INDEX (IXA_WPLATA__KONTRAHENT__PK))
"""

@pytest.mark.version('>=3.0.5')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
