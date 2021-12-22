#coding:utf-8
#
# id:           bugs.core_0972
# title:        Case insensitive collation for UTF-8
# decription:   Basic test for case-insensitive comparison of char and blob fields with text literals. Use non-ascii text here.
# tracker_id:   CORE-972
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         bugs.core_972

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('BLOB_ID .*', '')]

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- 2.5.8.27062: OK, 1.297s.
    -- 2.5.8.27065: OK, 0.719s.
    -- 3.0.3.32727: OK, 2.609s.
    -- 3.0.3.32738: OK, 1.375s.
    -- 4.0.0.651: OK, 2.547s.
    -- 4.0.0.680: OK, 1.141s.  
    
    create table test(fc varchar(50) collate unicode_ci, fb blob sub_type 1collate unicode_ci);
    commit;
    insert into test(fc,fb) values ('bibliothèque Éditeur', 'mêlés à des OBJETS DE L''EXTRÊME-Orient');
    insert into test(fc,fb) values ('bibliothÈque éditeur', 'MÊlés à des objETS DE l''extrême-orient');
    commit;
    set list on;
    set blob all;
    set count on;
    select fc as blob_id from test 
    where fc='BiblioTHÈQUE ÉDiteuR'
    
    UNION ALL
    
    select fb as blob_id from test 
    where fb 
        between 'MÊLÉS À DES OBJETS DE L''EXTRÊME-ORIENT' 
            and 'mÊLÉS À des objETS DE L''EXTRÊME-ORIENT'
    order by 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    bibliothèque Éditeur
    bibliothÈque éditeur
    mêlés à des OBJETS DE L'EXTRÊME-Orient
    MÊlés à des objETS DE l'extrême-orient 
    Records affected: 4 
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

