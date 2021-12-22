#coding:utf-8
#
# id:           bugs.core_3239
# title:        UTF8 UNICODE_CI collate can not be used in compound index
# decription:   
# tracker_id:   CORE-3239
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    create collation co_utf8_ci_ai for utf8 from unicode case insensitive accent insensitive; 
    commit;

    create table test (
        rule_id integer not null
        ,ci varchar(20) character set utf8 not null collate unicode_ci
        ,ciai varchar(20) character set utf8 not null collate co_utf8_ci_ai
        ,bfield boolean
        ,pattern varchar(10) character set none
        ,constraint test_pk  primary key (rule_id, ci, ciai) using index test_int_ci_ciai
        ,constraint test_unq unique(bfield, ciai, ci) using index test_bool_ciai_ci
    );
    commit;

    -- áéíóúý àèìòù âêîôû ãñõ äëïöüÿ çš δθλξσψω ąęłźż 
    insert into test (rule_id, ci, ciai, bfield, pattern) values (1, 'âêîôû' , 'âÊîôû' , true , '_e_O%');
    insert into test (rule_id, ci, ciai, bfield, pattern) values (2, 'äëïöüÿ', 'Äëïöüÿ', false, '_e%ioU_');
    insert into test (rule_id, ci, ciai, bfield, pattern) values (3, 'áéíóúý', 'ÁéÍÓÚý', false, 'A__O_Y');
    insert into test (rule_id, ci, ciai, bfield, pattern) values (4, 'àèìòù' , 'àÈÌòù' , true , '___O_');
    commit;

    set list on;
    set plan on;
    --set echo on;
    
    select rule_id
    from test
    where bfield = false and ciai similar to pattern;
    
    select rule_id 
    from test 
    where 
        rule_id = 1 
        and ci starting with 'ÂÊ'
        and ciai similar to '%EIOU%';

    select rule_id from test 
    where 
        bfield = false
        and ciai similar to 'AEIOUY'
        and ci similar to '%ÄË%ÜŸ';

    select a.rule_id
    from test a
    join test b on a.rule_id = b.rule_id and a.ciai = b.ci
    where a.bfield  = true;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST INDEX (TEST_BOOL_CIAI_CI))
    RULE_ID                         2
    RULE_ID                         3

    PLAN (TEST INDEX (TEST_INT_CI_CIAI))
    RULE_ID                         1

    PLAN (TEST INDEX (TEST_BOOL_CIAI_CI))
    RULE_ID                         2

    PLAN JOIN (A INDEX (TEST_BOOL_CIAI_CI), B INDEX (TEST_INT_CI_CIAI))
    RULE_ID                         1
    RULE_ID                         4
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

