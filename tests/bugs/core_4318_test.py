#coding:utf-8
#
# id:           bugs.core_4318
# title:        Regression: Predicates involving PSQL variables/parameters are not pushed inside the aggregation
# decription:   
# tracker_id:   CORE-4318
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t2 (
      id integer not null,
      t1_id integer
    );
    commit;
    
    recreate table t1 (
      id integer not null
    );
    commit;
    
    set term ^;
    
    execute block
    as
    declare variable i integer = 0;
    begin
      while (i < 1000) do begin
        i = i + 1;
    
        insert into t2(id, t1_id) values(:i, mod(:i, 10));
    
        merge into t1 using (
          select mod(:i, 10) as f from rdb$database
        ) src on t1.id = src.f
        when not matched then
           insert (id) values(src.f);
    
      end -- while (i < 1000) do begin
    
    end^
    set term ;^
    commit;
    
    alter table t1 add constraint pk_t1 primary key (id);
    alter table t2 add constraint pk_t2 primary key (id);
    alter table t2 add constraint fk_t2_ref_t1 foreign key (t1_id) references t1(id);
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set explain on;
    set planonly;
    
    set term ^;
    execute block
    returns (
      s integer
    )
    as
    declare variable v integer = 1;
    begin
      with t as (
        select t1_id as t1_id, sum(id) as s
        from t2
        group by 1
      )
      select s
      from t
      where t1_id = :v
      into :s;
    
      suspend;
    end
    ^
    set term ;^
    -- In 3.0.0.30837 plan was:
    -- Select Expression
    --    -> Singularity Check
    --        -> Filter
    --            -> Aggregate
    --                -> Table "T T2" Access By ID
    --                    -> Index "FK_T2_REF_T1" Scan 
    -- (i.e. there was NO "Filter" between "Aggregate" and "Table "T T2" Access By ID")
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Select Expression
        -> Singularity Check
            -> Filter
                -> Aggregate
                    -> Filter
                        -> Table "T2" as "T T2" Access By ID
                            -> Index "FK_T2_REF_T1" Range Scan (full match)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

