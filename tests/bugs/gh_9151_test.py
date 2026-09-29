#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9151
TITLE:       Regression in 5.0.4: "no current record for fetch operation" on a LEFT JOIN to an aggregated derived table
DESCRIPTION:
NOTES:
    [29.09.2026] pzotov
    Confirmed bug on 6.0.0.2182-c55ce22; 5.0.5.1888-9b169bc.
    Checked on 6.0.0.2183-84f30a5; 5.0.5.1889-d81ee3f; also: 6.0.0.2187; 5.0.5.1895; 4.0.8.3320; 3.0.15.33889
"""
import os
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=3.0')
def test_1(act: Action):

    test_script = f"""
        set bail on;
        create table company (
            id integer not null
            ,code varchar(20)
        );

        create table sale (
            id integer not null
            ,company_id integer not null
            ,mon integer
            ,amount numeric(15,2)
        );

        create table ret (
            sale_id integer not null
            ,company_id integer not null
        );
        commit;

        insert into company values (1, '00000000000001');
        insert into company values (2, '00000000000002');

        insert into sale values (1, 1, 1, 100);
        insert into sale values (2, 2, 1, 100);
        insert into sale values (3, 1, 2, 100);
        insert into sale values (4, 2, 2, 100);
        insert into sale values (5, 1, 3, 100);
        insert into sale values (6, 2, 3, 100);
        insert into sale values (7, 1, 4, 100);

        insert into ret values (1, 1);
        insert into ret values (4, 2);
        insert into ret values (101, 1);
        insert into ret values (102, 1);
        insert into ret values (103, 1);
        insert into ret values (104, 1);
        insert into ret values (105, 1);
        insert into ret values (106, 1);
        insert into ret values (107, 1);
        insert into ret values (108, 1);
        insert into ret values (109, 1);
        insert into ret values (110, 1);
        insert into ret values (111, 1);
        insert into ret values (112, 1);
        insert into ret values (113, 1);
        insert into ret values (114, 1);
        insert into ret values (115, 1);
        insert into ret values (116, 1);
        insert into ret values (117, 1);
        insert into ret values (118, 1);
        commit;

        alter table company add constraint pk_company primary key(id);
        alter table sale add constraint pk_sale primary key(id, company_id);
        alter table ret add constraint pk_ret primary key(sale_id, company_id);
        create index ix_company_code on company (code);
        commit;

        set list on;
        set count on;
        select v.code, v.mon, v.sold, d.returned
        from
          (select c.code, s.mon, sum(s.amount) sold
           from sale s
             join company c on (c.id = s.company_id)
           group by 1, 2) v
          left join
          (select c.code, s.mon, sum(s.amount) returned
           from sale s
             join ret r on (r.sale_id = s.id and r.company_id = s.company_id)
             join company c on (c.id = s.company_id)
           group by 1, 2) d
          on (d.code = v.code and d.mon = v.mon)
        order by 1,2,3,4
        ;
    """

    act.expected_stdout = """
        CODE 00000000000001
        MON 1
        SOLD 100.00
        RETURNED 100.00
        CODE 00000000000001
        MON 2
        SOLD 100.00
        RETURNED <null>
        CODE 00000000000001
        MON 3
        SOLD 100.00
        RETURNED <null>
        CODE 00000000000001
        MON 4
        SOLD 100.00
        RETURNED <null>
        CODE 00000000000002
        MON 1
        SOLD 100.00
        RETURNED <null>
        CODE 00000000000002
        MON 2
        SOLD 100.00
        RETURNED 100.00
        CODE 00000000000002
        MON 3
        SOLD 100.00
        RETURNED <null>

        Records affected: 7
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
