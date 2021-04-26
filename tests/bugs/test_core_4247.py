#coding:utf-8
#
# id:           bugs.core_4247
# title:        Delete "where current of" cursor fails for tables with newly added fields
# decription:   Scenario has been taken from attachment to this ticket
# tracker_id:   CORE-4247
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """
    create table test_table (id  integer not null, desc varchar(10));
    alter table test_table add constraint pk_test_table primary key (id);
    commit;
    
    insert into test_table (id, desc) values (1, 'a');
    insert into test_table (id, desc) values (2, 'b');
    insert into test_table (id, desc) values (3, 'c');
    insert into test_table (id, desc) values (4, 'd');
    insert into test_table (id, desc) values (5, 'e');
    insert into test_table (id, desc) values (6, 'f');
    insert into test_table (id, desc) values (7, 'g');
    insert into test_table (id, desc) values (8, 'h');
    insert into test_table (id, desc) values (9, 'i');
    insert into test_table (id, desc) values (10, 'k');
    commit;
    
    alter table test_table add seqno integer;
    commit;
    
    -- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    -- without this update  - everything works
    update test_table set seqno=id where id>=5;
    commit;
     
    set term ^ ;
    create or alter procedure test_cursor
    as
    declare variable id integer;
    declare variable desc varchar(10);
    declare variable seqno integer;
    begin
        for
          select  id, desc, seqno from test_table
          order by seqno  -- if seqno values are unique - it works. With "order by id" works
          into
            :id, :desc, :seqno
          as cursor data_cursor
        do begin
          delete from test_table where current of data_cursor; -- this fails !!!
          -- with dummy suspend stored procedure works even it does not require to return any results
          --suspend;
        end
    end^
    set term ; ^
    
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    execute procedure test_cursor;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.3')
def test_core_4247_1(act_1: Action):
    act_1.execute()

