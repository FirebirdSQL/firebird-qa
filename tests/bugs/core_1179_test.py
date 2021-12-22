#coding:utf-8
#
# id:           bugs.core_1179
# title:        "CH" and "LL" are not separate spanish alphabet letters since 1994
# decription:   
# tracker_id:   CORE-1179
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test_utf8(id int, esp varchar(10));
    commit;
    
    insert into test_utf8 values(-2,'CH');
    insert into test_utf8 values(-1,'LL');
    insert into test_utf8 values( 1,'C');
    insert into test_utf8 values( 2,'CA');
    insert into test_utf8 values( 3,'CZ');
    insert into test_utf8 values( 5,'D');
    
    insert into test_utf8 values( 6,'L');
    insert into test_utf8 values( 7,'LA');
    insert into test_utf8 values( 8,'LZ');
    insert into test_utf8 values(10,'M');
    commit;

    recreate table test_iso( id int, esp varchar(10) character set ISO8859_1 );
    commit;


    insert into test_iso values(-2,'CH');
    insert into test_iso values(-1,'LL');
    insert into test_iso values( 1,'C');
    insert into test_iso values( 2,'CA');
    insert into test_iso values( 3,'CZ');
    insert into test_iso values( 5,'D');
    
    insert into test_iso values( 6,'L');
    insert into test_iso values( 7,'LA');
    insert into test_iso values( 8,'LZ');
    insert into test_iso values(10,'M');
    commit;

    select id, esp from test_utf8 order by esp collate utf8;
    select id, esp from test_iso order by esp collate es_es;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
              ID ESP        
    ============ ========== 
               1 C          
               2 CA         
              -2 CH         
               3 CZ         
               5 D          
               6 L          
               7 LA         
              -1 LL         
               8 LZ         
              10 M          
    
    
              ID ESP        
    ============ ========== 
               1 C          
               2 CA         
              -2 CH         
               3 CZ         
               5 D          
               6 L          
               7 LA         
              -1 LL         
               8 LZ         
              10 M          
"""

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

