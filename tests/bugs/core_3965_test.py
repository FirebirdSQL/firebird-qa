#coding:utf-8
#
# id:           bugs.core_3965
# title:        Creating a procedure containing "case when" expression leads to a server crash
# decription:   
# tracker_id:   CORE-3965
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='employee-ods12.fbk', init=init_script_1)

test_script_1 = """
    -- Table 'sales' for this SP is taken from standard samples database 'employee.fdb' which comes with every FB build.
    set term ^;
    create or alter procedure p_beteiligung_order (
        gid char(36) character set iso8859_1 collate iso8859_1,
        ordernr integer,
        dir smallint,
        mit_fuehrender char(1) character set iso8859_1 collate iso8859_1)
    as
    declare variable cur_ordernr integer;
    declare variable max_ordernr integer;
    declare variable fk_ref char(36);
    begin
    
      if (mit_fuehrender is null) then
        mit_fuehrender = 'F';
    
      
      select r.qty_ordered, r.item_type
      from sales r
      where r.po_number = :gid
      into :cur_ordernr, :fk_ref;
      
      if (ordernr is null) then
        ordernr = cur_ordernr + coalesce(dir, 0);
    
      if (ordernr <= case mit_fuehrender
                       when 'T' then 1
                       else 2
                     end) then
        ordernr = case mit_fuehrender
                    when 'T' then 1
                    else 2
                  end;
      else
      begin
        select max(r.qty_ordered)
        from sales r
        where r.item_type = :fk_ref
        into :max_ordernr;
        if (ordernr > max_ordernr) then
          ordernr = max_ordernr;
      end
    
      if (ordernr = cur_ordernr) then
        exit;
      else
      if (ordernr < cur_ordernr) then
        update sales r
        set r.qty_ordered = r.qty_ordered + 1
        where r.item_type = :fk_ref and
              r.qty_ordered between :ordernr and :cur_ordernr;
      else
        update sales r
        -- ::: NB ::: in the ticket it was: "set r.qty_ordered = r.ordernr - 1" - but there is NO such field in the table SALES!
        set r.qty_ordered = :ordernr - 1 
        where r.qty_ordered = :fk_ref and
              r.qty_ordered between :cur_ordernr and :ordernr;
    
      update sales r
      set r.qty_ordered = :ordernr
      where r.po_number = :gid;
    
    end^
    set term ;^
    commit;

    drop procedure p_beteiligung_order;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

