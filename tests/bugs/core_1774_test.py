#coding:utf-8
#
# id:           bugs.core_1774
# title:        Problem with COLLATE ES_ES_CI_AI
# decription:   
# tracker_id:   CORE-1774
# min_versions: ['2.0.7']
# versions:     2.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='ISO8859_1', sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table table_a (
        field_a varchar(100) character set iso8859_1 collate es_es_ci_ai
    );
    commit;
    insert into table_a (field_a) values ('Hace buena noche');
    insert into table_a (field_a) values ('Voy a hacer de comer');
    insert into table_a (field_a) values ('The web is hacked');
    commit;
    
    set list on;
    select * from table_a where field_a like '%HACK%';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    FIELD_A                         The web is hacked
"""

@pytest.mark.version('>=2.0.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

