#coding:utf-8
#
# id:           bugs.core_2833
# title:        Changing data that affects an expression index that contains references to null date fields fails
# decription:   
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         bugs.core_2833

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table policen_order (
        id integer not null,
        vstatus integer,
        ablauf date,
        vstorno integer,
        storno date
    );
    alter table policen_order add constraint pk_new_table primary key (id);
    
    set term ^;
    execute block as
    begin
        execute statement 'drop sequence gen_policen_order_id';
    when any do begin end
    end
    ^
    set term ;^
    commit;
    create generator gen_policen_order_id;
    commit;
    
    set term ^;
    create or alter trigger policen_order_bi for policen_order
    active before insert position 0 as
    begin
      if (new.id is null) then
        new.id = gen_id(gen_policen_order_id,1);
    end
    ^
    set term ;^
    commit;
    
    -- insert some data with null dates
    insert into policen_order (id, vstatus, ablauf, vstorno, storno)
                       values (2, 1, null, null, null);
    insert into policen_order (id, vstatus, ablauf, vstorno, storno)
                       values (3, 2, null, null, null);
    insert into policen_order (id, vstatus, ablauf, vstorno, storno)
                       values (4, 3, null, null, null);
    commit;
    
    -- now let's create an obscure index
    
    create index idx_policen_order_bit_vstatus on policen_order
    computed by
    (
        case
            when policen_order.vstatus=1 then 64 -- anbahnung
            when policen_order.vstatus=7 then 32 -- da
            when policen_order.vstatus=8 then 16 -- angebot
            when policen_order.vstatus=0 then 8 -- vertrag
            when policen_order.vstatus=3 then 8 -- vertrag
            when policen_order.vstatus=4 then 8 -- vertrag
            when policen_order.vstatus=5 then 8 -- vertrag
            when policen_order.vstatus=6 then 8 -- vertrag
            when policen_order.vstatus=2 then 4 -- fremdvertrag
            else 0
        end
        +
        case
            when
                coalesce(policen_order.ablauf, current_date+1)<=current_date
                or
                policen_order.vstorno=1
                and coalesce(policen_order.storno, current_date+1) <= current_date
            then 2
            else 0
        end
    );
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    update policen_order set vstatus = 8 where id = 2;
    commit;
    select * from policen_order;
    update policen_order set vstatus = 2 where id = 2;
    commit;
    select * from policen_order;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              2
    VSTATUS                         8
    ABLAUF                          <null>
    VSTORNO                         <null>
    STORNO                          <null>
    
    ID                              3
    VSTATUS                         2
    ABLAUF                          <null>
    VSTORNO                         <null>
    STORNO                          <null>
    
    ID                              4
    VSTATUS                         3
    ABLAUF                          <null>
    VSTORNO                         <null>
    STORNO                          <null>
    
    
    
    ID                              2
    VSTATUS                         2
    ABLAUF                          <null>
    VSTORNO                         <null>
    STORNO                          <null>
    
    ID                              3
    VSTATUS                         2
    ABLAUF                          <null>
    VSTORNO                         <null>
    STORNO                          <null>
    
    ID                              4
    VSTATUS                         3
    ABLAUF                          <null>
    VSTORNO                         <null>
    STORNO                          <null>
  """

@pytest.mark.version('>=2.5')
def test_core_2833_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

