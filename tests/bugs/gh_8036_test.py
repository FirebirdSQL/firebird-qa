#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8036
TITLE:       "no current record for fetch operation" error with select stored procedures
DESCRIPTION:
NOTES:
    [10.03.2026] pzotov
    Issue has been fixed:
    * in 6.x:
        https://github.com/FirebirdSQL/firebird/commit/c5af128afbc7d0aee3e05097eb5fdc9419a9cb74
        "Attempt to fix #7937: Inner join raises error 'no current record for fetch operation'..."
    * in 5.x:
        https://github.com/FirebirdSQL/firebird/commit/b4b355978f7375b02727f291e3ca5c6550a1d66a
        "Backport bugfix for #7937: Inner join raises error 'no current record for fetch operation' ..."
    On 3.x and 4.x problem currently remains.

    Confirmed problem on 5.0.1.1416-ad0e5ce (14-jun-2024); 5.0.1.1347 (05-mar-2024); 6.0.0.279 (09-mar-2024)
    Checked on: 6.0.0.286 (12-mar-2024); 5.0.1.1416-b4b3559 (17-jun-2024); 6.0.0.1814, 5.0.4.1782.
"""
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    create table products (
        id int not null,
        description varchar(100),
        tax_id int
    );

    create table taxes (
        id int not null,
        description varchar(50)
    );

    create table taxes_percs (
        tax_id int not null,
        tax_date date not null,
        tax_perc numeric(9, 4) not null
    );
    commit;

    set term ^;
    create or alter procedure get_tax (tax_id int, tax_date date)
    returns (
        tax_id_ret int,
        tax_perc numeric(9, 4)
    ) as 
    begin
        select first 1 tax_id, tax_perc from taxes_percs
        where (tax_id = :tax_id) and (tax_date <= :tax_date)
        order by tax_date desc
        into :tax_id_ret, :tax_perc;
        suspend;
    end ^
    set term ;^
    commit;

    insert into products (id, description, tax_id) values (1, 'product 1', 1);
    insert into taxes (id, description) values (1, 'tax 1');
    insert into taxes (id, description) values (2, 'tax 2');
    insert into taxes_percs (tax_id, tax_date, tax_perc) values (1, '1-jan-2024', 1);
    commit;

    alter table taxes add constraint pk_taxes primary key (id);
    alter table products add constraint pk_products primary key (id);
    alter table taxes_percs add constraint pk_taxes_percs primary key (tax_id, tax_date);

    alter table products add constraint fk_products_1 foreign key (tax_id) references taxes (id) on update cascade on delete set null;
    alter table taxes_percs add constraint fk_taxes_percs_1 foreign key (tax_id) references taxes (id) on update cascade on delete cascade;
    commit;

    set list on;
    set count on;
    select p.id, p.description, t.tax_perc
    from products p 
    join get_tax(p.tax_id, current_date) t on (t.tax_id_ret = p.tax_id)
    ;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    ID                              1
    DESCRIPTION                     product 1
    TAX_PERC                        1.0000
    Records affected: 1
"""

@pytest.mark.version('>=5.0.1')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
