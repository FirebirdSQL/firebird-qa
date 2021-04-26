#coding:utf-8
#
# id:           bugs.core_4180
# title:        CREATE COLLATION does not verify base collation charset
# decription:   
# tracker_id:   CORE-4180
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table tci(id int);
    commit;
    
    set term ^;
    execute block as
    begin
      begin
        execute statement 'drop collation ci_coll';
      when any do begin end
      end
    
      begin
        execute statement 'drop collation win1252_unicode';
      when any do begin end
      end
    end
    ^ set term ;^
    commit;
    
    create collation win1252_unicode for win1252; -- this is special collation named (charset_unicode)
    create collation ci_coll for win1252 from win1252_unicode case insensitive;
    commit;
    
    recreate table tci(id int, name varchar(30) character set win1252 collate ci_coll);
    commit;
    insert into tci(id, name) values(9, 'one Row');
    insert into tci(id, name) values(7, 'One row');
    insert into tci(id, name) values(0, 'oNE row');
    insert into tci(id, name) values(1, 'one ROw');
    insert into tci(id, name) values(5, 'one roW');
    insert into tci(id, name) values(4, 'oNe roW');
    insert into tci(id, name) values(2, 'onE ROw');
    insert into tci(id, name) values(3, 'ONE ROW');
    insert into tci(id, name) values(8, 'oNE rOW');
    insert into tci(id, name) values(1, 'one row');
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select n1, n2, min(n1) n3, max(n2) n4
    from (
      select n1, n2
      from (
        select min(name) n1, max(name) n2 from tci group by name
        union all
        select distinct name, name from tci
        union all
        select distinct max(name), max(name) from tci
      )
      order by rand()
    )
    group by n1, n2;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
N1                              one row
N2                              one row
N3                              ONE ROW
N4                              ONE ROW
  """

@pytest.mark.version('>=3.0')
def test_core_4180_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

