#coding:utf-8
#
# id:           bugs.core_4846
# title:        Altering a trigger indicating other table than the original does not reflect the change
# decription:   
# tracker_id:   CORE-4846
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
    begin
        execute statement 'drop trigger muddy_trg';
    when any do begin end
    end
    ^
    set term ;^
    commit;
    
    recreate table test1( id1 int primary key, x1 int);
    recreate table test2( id2 int primary key, x2 int);
    recreate sequence g;
    commit;
    
    set term ^;
    create or alter trigger muddy_trg for test2 active before insert position 23184 as
    begin
        new.id2 = coalesce( new.id2, gen_id(g, 1) );
    end
    ^
    set term ;^
    commit;
    show trigger muddy_trg;
    

    -- Following statements failed on 3.0.0.31907 with:
    -- Statement failed, SQLSTATE = 42S22
    -- invalid request BLR at offset 17
    -- -column ID1 is not defined in table TEST2
    -- Passes OK on LI-V3.0.0.31916 Firebird 3.0 Release Candidate 1.

    set term ^;
    create or alter trigger muddy_trg for test1 inactive before insert position 17895  as
    begin
        new.id1 = coalesce( new.id1, gen_id(g, 1) );
    end
    ^
    set term ;^
    commit;
    show trigger muddy_trg;
    
    set term ^;
    recreate trigger muddy_trg for test2 inactive after delete position 11133 as
    begin
        insert into test1(id1, x1) values(old.id2, old.x2);
    end
    ^
    set term ;^
    commit;
    show trigger muddy_trg;
    
    
    set term ^;
    recreate trigger muddy_trg for test1 active before delete or update or insert position 24187 as
    begin
        if (not inserting) then insert into test2(id2, x2) values(old.id1, old.x1);
        else insert into test2(id2, x2) values(new.id1, new.x1);
    end
    ^
    set term ;^
    commit;
    show trigger muddy_trg;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Triggers on Table TEST2:
    MUDDY_TRG, Sequence: 23184, Type: BEFORE INSERT, Active
    as
    begin
        new.id2 = coalesce( new.id2, gen_id(g, 1) );
    end

    
    Triggers on Table TEST1:
    MUDDY_TRG, Sequence: 17895, Type: BEFORE INSERT, Inactive
    as
    begin
        new.id1 = coalesce( new.id1, gen_id(g, 1) );
    end
    
    Triggers on Table TEST2:
    MUDDY_TRG, Sequence: 11133, Type: AFTER DELETE, Inactive
    as
    begin
        insert into test1(id1, x1) values(old.id2, old.x2);
    end
    
    Triggers on Table TEST1:
    MUDDY_TRG, Sequence: 24187, Type: BEFORE DELETE OR UPDATE OR INSERT, Active
    as
    begin
        if (not inserting) then insert into test2(id2, x2) values(old.id1, old.x1);
        else insert into test2(id2, x2) values(new.id1, new.x1);
    end
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

