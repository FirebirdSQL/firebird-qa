#coding:utf-8
#
# id:           bugs.core_0143
# title:        Using where params in SUM return incorrect results
# decription:
#                   30.10.2019. NB: new datatype in FB 4.0 was introduces: numeric(38,0).
#                   It can lead to additional ident of values when we show them in form "SET LIST ON",
#                   so we have to ignore all internal spaces - see added 'substitution' section below.
#                   Checked on:
#                       4.0.0.1635 SS: 1.061s.
#                       3.0.5.33182 SS: 0.754s.
#                       2.5.9.27146 SC: 0.190s.
#
# tracker_id:   CORE-0143
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table yeardata
    (
      id integer not null,
      ayear integer,
      avalue numeric( 18, 2),
     constraint pk_yeardata primary key (id)
    );
    commit;

    insert into yeardata(id, ayear, avalue) values (1, 2005, 3.40);
    insert into yeardata(id, ayear, avalue) values (2, 2005, 6.60);
    insert into yeardata(id, ayear, avalue) values (3, 2004, 5.20);
    insert into yeardata(id, ayear, avalue) values (4, 2004, 5.80);
    insert into yeardata(id, ayear, avalue) values (5, 2004, 5.00);
    commit;

    set list on;
    select
         sum(case when ayear = 2004 then avalue else null end) as avalue_2004_1
        ,sum(case when ayear = 2005 then avalue else null end) as avalue_2005_1
    from yeardata;

    set term ^;
    execute block returns( avalue_2004_2 numeric( 18, 2), avalue_2005_2 numeric( 18, 2)) as
    begin
        execute statement
        (
            'select
                 sum(case when ayear = ? then avalue else null end)
                ,sum(case when ayear = ? then avalue else null end)
            from yeardata'
        ) ( 2004, 2005 )
        into avalue_2004_2, avalue_2005_2;
        suspend;
    end
    ^
    set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    AVALUE_2004_1                   16.00
    AVALUE_2005_1                   10.00
    AVALUE_2004_2                   16.00
    AVALUE_2005_2                   10.00
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

