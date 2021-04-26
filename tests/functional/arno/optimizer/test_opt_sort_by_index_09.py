#coding:utf-8
#
# id:           functional.arno.optimizer.opt_sort_by_index_09
# title:        ORDER BY ASC using index (non-unique)
# decription:   ORDER BY X
#               If WHERE clause is present it should also use index if possible.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.arno.optimizer.opt_sort_by_index_09

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """
    create table table_66 (id integer);
    commit;
    set term ^ ;
    create procedure pr_filltable_66 as
      declare fillid integer;
    begin
      fillid = 2147483647;
      while (fillid > 0) do
      begin
        insert into table_66 (id) values (:fillid);
        fillid = fillid / 2;
      end
      insert into table_66 (id) values (null);
      insert into table_66 (id) values (0);
      insert into table_66 (id) values (null);
      fillid = -2147483648;
      while (fillid < 0) do
      begin
        insert into table_66 (id) values (:fillid);
        fillid = fillid / 2;
      end
    end
    ^
    set term ; ^
    commit;
    
    execute procedure pr_filltable_66;
    commit;
    
    create asc index i_table_66_asc on table_66 (id);
    create desc index i_table_66_desc on table_66 (id);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Queries with RANGE index scan now have in the plan only "ORDER"
    -- clause (index navigation) without bitmap building.
    -- See: http://tracker.firebirdsql.org/browse/CORE-1550
    -- ("the same index should never appear in both ORDER and INDEX parts of the same plan item")

    -- :::::::::::::::::::::::::::::::::::::::::::::::
    -- do *NOT* use SET E`XPLAIN untill extremely need. 
    -- Always consult with Dmitry before doing this!
    -- :::::::::::::::::::::::::::::::::::::::::::::::

    set plan on; 

    select id as id_asc
    from table_66 t66
    where t66.id between -20 and 20
    order by t66.id asc;

    select id as id_desc
    from table_66 t66
    where t66.id between -20 and 20
    order by t66.id desc;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T66 ORDER I_TABLE_66_ASC)
    ID_ASC
       -16
        -8
        -4
        -2
        -1
         0
         1
         3
         7
        15

    PLAN (T66 ORDER I_TABLE_66_DESC)
    ID_DESC
         15
          7
          3
          1
          0
         -1
         -2
         -4
         -8
        -16
  """

@pytest.mark.version('>=3.0')
def test_opt_sort_by_index_09_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

