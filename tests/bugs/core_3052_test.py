#coding:utf-8
#
# id:           bugs.core_3052
# title:        Wrong resultset
# decription:   Empty rowset when selecting from table with compound index on PXW_HUNDC-collated fields
# tracker_id:   CORE-3052
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='WIN1250', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- NB: do NOT downgrate minimal version to 2.5 - at least for 2.5.4.26857
    -- following queries return zero rows.

    create domain xvar10n as varchar(160) character set WIN1250 not null collate PXW_HUNDC;
    create domain xint as int;
    commit;

    create table tmp_test (
        m1 xvar10n
       ,m2 xvar10n
       ,val xint
    );
    commit;

    alter table tmp_test add constraint tmp_test_uk1 unique (m1, m2);
    commit;

    insert into tmp_test (m1, m2, val) values ('A', 'C1', 1);
    insert into tmp_test (m1, m2, val) values ('A', 'C2', 2);
    insert into tmp_test (m1, m2, val) values ('A', 'D2', 3);
    insert into tmp_test (m1, m2, val) values ('A', 'M3', 3);

    set list on;
    select *
    from tmp_test te
    where te.m1 = 'A' and te.m2 like 'C%';

    select *
    from tmp_test te
    where te.m1 = 'A' and te.m2 like 'D%';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    M1                              A
    M2                              C1
    VAL                             1

    M1                              A
    M2                              C2
    VAL                             2

    M1                              A
    M2                              D2
    VAL                             3
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

