#coding:utf-8
#
# id:           bugs.core_4867
# title:        Server crash when preparing a query with PLAN clause at some CTE
# decription:   
# tracker_id:   CORE-4867
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Tested on:
    -- LI-V2.5.5.26910 after commit http://sourceforge.net/p/firebird/code/61955
    -- LI-V3.0.0.31924

    recreate table table1 (
      field1 integer not null
    );

    recreate table table2 (
      field1 integer not null,
      date1 date not null
    );

    insert into table1 values(1);
    insert into table2 values(1, date '30.06.2015');
    insert into table2 values(1, date '31.05.2015');
    insert into table2 values(1, date '31.07.2015');

    insert into table1 values(2);
    insert into table2 values(2, date '31.03.2012');
    insert into table2 values(2, date '29.05.2012');
    insert into table2 values(2, date '31.01.2012');
    commit;

    alter table table1 add constraint pk_table1 primary key (field1);
    alter table table2 add constraint pk_table2 primary key (field1, date1)
      using descending index pk_table2;
    create index idx_table2 on table2 (field1, date1);
    commit;

    set list on;
    with aa
    as (select t1.field1,
               (select first 1 t2.date1
                  from table2 t2
                 where t2.field1 = t1.field1
                plan(t2 index(idx_table2))
                order by t2.field1 asc, t2.date1 asc) as date1
          from table1 t1)

    select date1, count('x')
      from aa
    group by 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DATE1                           2012-01-31
    COUNT                           1

    DATE1                           2015-05-31
    COUNT                           1
"""

@pytest.mark.version('>=2.5.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

