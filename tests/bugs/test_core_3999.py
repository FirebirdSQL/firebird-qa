#coding:utf-8
#
# id:           bugs.core_3999
# title:        Bug in unique constraints and / or NUMERIC-SORT collation
# decription:   
#                   Confirmed on WI-V2.5.7.27026, it issues:
#                   Statement failed, SQLSTATE = 23000
#                   violation of PRIMARY or UNIQUE KEY constraint "UK_PRODUCTS" on table "PRODUCTS"
#                
# tracker_id:   CORE-3999
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table products(productno char(1));
    commit;
    set term ^;
    execute block as
    begin
      execute statement 'drop collation unicode_num_ci_ai';
      when any do begin end
    end^
    set term ;^
    commit;
    create collation unicode_num_ci_ai for utf8 from unicode_ci_ai 'numeric-sort=1';
    recreate table products(productno varchar(100) character set utf8 collate unicode_num_ci_ai);
    alter table products add constraint uk_products unique (productno) using index uk_products; 
    commit;
    insert into products values('s01');
    insert into products values('s1');
    insert into products values('01');
    insert into products values('001');
    insert into products values('-01');
    insert into products values('-001');
    commit;
    set list on;
    select distinct productno from products;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PRODUCTNO                       -001
    PRODUCTNO                       -01
    PRODUCTNO                       001
    PRODUCTNO                       01
    PRODUCTNO                       s01
    PRODUCTNO                       s1
  """

@pytest.mark.version('>=3.0')
def test_core_3999_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

