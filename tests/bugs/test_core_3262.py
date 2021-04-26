#coding:utf-8
#
# id:           bugs.core_3262
# title:        LIST() may overwrite last part of output with zero characters
# decription:   
# tracker_id:   CORE-3262
# min_versions: ['2.1.4']
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table vc (s varchar(8000));
    commit;
    
    insert into vc values (cast('A' as char(4000)) || 'B');
    
    set list on;
    
    select char_length(s), position('A' in s), position('B' in s) from vc;
    
    with q (l) as (select list(s) from vc)
      select char_length(l), position('A' in l), position('B' in l) from q;
    
    
    update vc set s = (cast('A' as char(5000)) || 'B');
    
    select char_length(s), position('A' in s), position('B' in s) from vc;
    
    
    with q (l) as (select list(s) from vc)
      select char_length(l), position('A' in l), position('B' in l) from q;
    
    
    with q (l) as (select reverse(list(s)) from vc)
      select char_length(l), position('A' in l), position('B' in l) from q;
    
    with q (l) as (select list(s) from vc)
      select ascii_val(substring(l from 4066 for 1)), ascii_val(substring(l from 4067 for 1)) from q;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CHAR_LENGTH                     4001
    POSITION                        1
    POSITION                        4001

    CHAR_LENGTH                     4001
    POSITION                        1
    POSITION                        4001

    CHAR_LENGTH                     5001
    POSITION                        1
    POSITION                        5001

    CHAR_LENGTH                     5001
    POSITION                        1
    POSITION                        5001
    
    CHAR_LENGTH                     5001
    POSITION                        5001
    POSITION                        1

    ASCII_VAL                       32
    ASCII_VAL                       32
  """

@pytest.mark.version('>=2.1.4')
def test_core_3262_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

