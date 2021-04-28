#coding:utf-8
#
# id:           bugs.core_4419
# title:        Server crashes while sorting records longer than 128KB
# decription:   
# tracker_id:   CORE-4419
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """
    recreate table lines1 (line varchar(2000));
    
    insert into lines1 (line) values('2007' || ascii_char(9) || 'abcabcabc' || ascii_char(9) || 'xx');
    insert into lines1 (line) values('2007' || ascii_char(9) || 'defdefdef' || ascii_char(9) || 'xx');
    insert into lines1 (line) values('2007' || ascii_char(9) || 'ghighighi' || ascii_char(9) || 'xx');
    insert into lines1 (line) values('2008' || ascii_char(9) || 'defdefdef' || ascii_char(9) || 'xx');
    
    -- note that spaces between line values should be tabs, 	, ascii_char(9)
    commit;
    
    recreate table lines2 (line varchar(2000));
    
    insert into lines2 (line) values('2007' || ascii_char(9) || 'abcabcabc' || ascii_char(9) || 'xx');
    insert into lines2 (line) values('2007' || ascii_char(9) || 'defgdefg'  || ascii_char(9) || 'xx');
    insert into lines2 (line) values('2007' || ascii_char(9) || 'ghighighi' || ascii_char(9) || 'xx');
    insert into lines2 (line) values('2008' || ascii_char(9) || 'abcabcabc' || ascii_char(9) || 'xx');
    insert into lines2 (line) values('2008' || ascii_char(9) || 'defdefdef' || ascii_char(9) || 'xx');
    commit;
    
    
    set term ^;
    create function split (
      s varchar(32000),
      n integer = 1
    )
    returns varchar(32000)
    as
    declare startpos integer;
    declare pos integer;
    begin
        -- extract tab separated parts from string
        pos = 0;
        while (n > 0) do
        begin
            startpos = pos + 1;
            pos = position(ascii_char(9), :s, :startpos);
            if (pos = 0) then break;
            n = n - 1;
        end
        if (pos > 0) then
            return nullif(substring(s from :startpos for pos - startpos), '');
        -- get part after last tab
        else if (n = 1) then
            return nullif(substring(s from :startpos), '');
    end
    ^
    set term ;^
    commit;

    set list on;
    select u.f1, u.f2
    from (select split(line) f1, split(line, 2) f2 from lines1
          union
          select split(line), split(line, 2) from lines2) u
    join (select split(line) f1, split(line, 2) f2 from lines1) a on a.f1 = u.f1 and a.f2 = u.f2
    join (select split(line) f1, split(line, 2) f2 from lines2) b on b.f1 = u.f1 and b.f2 = u.f2
    order by 1, 2;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F1                              2007
    F2                              abcabcabc

    F1                              2007
    F2                              ghighighi

    F1                              2008
    F2                              defdefdef
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

