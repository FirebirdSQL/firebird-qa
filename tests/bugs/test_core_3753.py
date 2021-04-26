#coding:utf-8
#
# id:           bugs.core_3753
# title:        The trigger together with the operator MERGE if in a condition of connection ON contains new is not compiled
# decription:   
# tracker_id:   CORE-3753
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
    begin
        begin execute statement 'drop trigger horse_ai'; when any do begin end end
    end
    ^
    set term ;^
    
    recreate table cover(id int);
    commit;
    
    recreate table horse (
        code_horse integer constraint pk_horse primary key,
        code_father integer default -2 not null,
        code_mother integer default -3 not null,
        name varchar(50)
    );
    
    recreate table cover (
        code_cover integer constraint pk_cover primary key
        ,code_father integer not null
        ,code_mother integer not null
        ,code_horse integer not null
        ,constraint fk_cover_ref_father foreign key (code_father) references horse (code_horse)
        ,constraint fk_cover_ref_horse foreign key (code_horse) references horse (code_horse)
        ,constraint fk_cover_ref_mother foreign key (code_mother) references horse (code_horse)
    );
    commit;
    
    set term ^;
    create or alter trigger horse_ai for horse active after insert position 0 as
    begin
        merge into cover
        using rdb$database as tbl
        on cover.code_father = new.code_father and
           cover.code_mother = new.code_mother
        when matched then
          update set
          code_horse = new.code_horse
        when not matched then
          insert (code_horse,
                  code_father,
                  code_mother)
          values (new.code_horse,
                  new.code_father,
                  new.code_mother);
    end
    ^
    set term ;^
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1.7')
def test_core_3753_1(act_1: Action):
    act_1.execute()

