#coding:utf-8
#
# id:           bugs.core_0085
# title:        Query with not in (select) returns wrong result
# decription:   
# tracker_id:   CORE-0085
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Results are OK since 2.1.7 up to 4.0.0
    -- Confirmed wrong result on 1.5.6

    set term ^;
    create or alter procedure tst1
    returns (packages integer)
    as
    begin
        packages=1;
        suspend;
        packages=2;
        suspend;
    end^
    set term ;^
    
    recreate table frrates1 (
        frrates1 integer not null,
        packages integer,
        primary key(frrates1)
    );
    commit;
    
    create index idx_frrates1_packages on frrates1 (packages);
    commit;
    
    recreate table schedpkgs1 (
        schedpkgs1 integer not null,
        schedule integer,
        frrates1 integer,
        primary key (schedpkgs1)
    );
    commit;
    
    create index idx_schedpkgs1_schedule on schedpkgs1 (schedule);
    commit;
    
    insert into frrates1 (frrates1, packages) values (11, 1);
    insert into frrates1 (frrates1, packages) values (12, 2);
    /* second record is essential (must exist in tst1) */
    commit;
    
    insert into schedpkgs1 (schedpkgs1, schedule, frrates1) values(21, 16651,11);
    insert into schedpkgs1 (schedpkgs1, schedule, frrates1) values(22, 16651,null); 
    /* important null value */
    commit;


    set count on;
    set list on;
    
    --    sub-query to be used later in sub-select,
    --    correctly uses frrates1 primary key index fr index (rdb$primary121),
    --    correctly returns (1)
    
    select fr.packages
      from schedpkgs1 sp
      join frrates1 fr on fr.frrates1=sp.frrates1
      where sp.schedule = 16651;
    
    --    1. results from stored procedure (1, 2),
    --    filtered out by sub-select query (1),
    --    expected results -- (2),
    --    ib5.6 correctly uses frrates1 primary key index fr index (rdb$primary121),
    --    ib5.6 returns correct results (2),
    --    problem -- fb1.5.3/2.0rc2 does not return anything,
    --    problem -- fb1.5.3/2.0rc2 uses wrong frrates1
    --    index fr index (idx_frrates1_packages)
    
    select packages
      from tst1
      where packages not in (select fr.packages
                               from schedpkgs1 sp
                               join frrates1 fr on
    fr.frrates1=sp.frrates1
                               where sp.schedule = 16651);
    
    --    2a. adding additional filter in sub-select query
    --    'fr.packages>0' fb1.5.3 still uses questionable frrates1 index fr
    --    index (idx_frrates1_packages) but results are as expected (2)
    
    select packages
      from tst1
      where packages not in (select fr.packages
                               from schedpkgs1 sp
                               join frrates1 fr on
    fr.frrates1=sp.frrates1
                               where sp.schedule = 16651
    and fr.packages>0);
    
    --    2b. replacing "not in" with "<> any" will return
    --    expected result and uses expected indices
    
    select t.packages
      from tst1 t
      where t.packages <> all (select fr.packages
                               from schedpkgs1 sp
                               join frrates1 fr on
    fr.frrates1=sp.frrates1
                               where sp.schedule = 16651);
    
    --    3. using table instead of stored procedure in main
    --    query, both ib5.6 and fb1.5.3 uses questionable frrates1
    --    index fr index (idx_frrates1_packages),
    --    and results are wrong, i.e. does not return (2)
    
    select f2.packages
    from frrates1 f2
    where f2.packages not in
        (
            select fr.packages
            from schedpkgs1 sp
            join frrates1 fr on
            fr.frrates1=sp.frrates1
            where sp.schedule = 16651
        );
    
    
    --    4a. adding the same additional filter
    --    'fr.packages>0' in sub-select query,
    --    incorrect results in ib5.6 (no results) (fr index
    --    (rdb$primary121,idx_frrates1_packages)),
    --    correct results in fb1.5.3 (returns 2)
    --    fb1.5.3 still uses questionable frrates1 index fr
    --    index (idx_frrates1_packages)
    
    
    select f2.packages
    from frrates1 f2
    where f2.packages not in
        (
            select fr.packages
            from schedpkgs1 sp
            join frrates1 fr on
            fr.frrates1=sp.frrates1
            where sp.schedule = 16651
            and fr.packages > 0
        );
    
    -- 4b. and again, the same query with <> any instead
    -- not in works correctly
    
    select f2.packages
    from frrates1 f2
    where f2.packages <> all
        (
            select fr.packages
            from schedpkgs1 sp
            join frrates1 fr on
            fr.frrates1=sp.frrates1
            where sp.schedule = 16651
        );
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PACKAGES                        1
    Records affected: 1
    PACKAGES                        2
    Records affected: 1
    PACKAGES                        2
    Records affected: 1
    PACKAGES                        2
    Records affected: 1
    PACKAGES                        2
    Records affected: 1
    PACKAGES                        2
    Records affected: 1
    PACKAGES                        2
    Records affected: 1
  """

@pytest.mark.version('>=2.5')
def test_core_0085_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

