#coding:utf-8
#
# id:           functional.gtcs.isql_show_command_collation
# title:        GTCS/tests/CF_ISQL_20. Misplaced collation when extracting metadata with isql
# decription:   
#               	::: NB ::: 
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_20.script
#               
#                   bug #223126 Misplaced collation when extracting metadata with isql
#               
#                   Checked on: 4.0.0.1803 SS; 3.0.6.33265 SS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain domain_with_collate_clause as char(1)
        character set iso8859_1
        default 'v'
        check(value >='a' and value <='z')
        collate es_es;

    create table table_with_collated_field (
        field_01 domain_with_collate_clause
            default 'w'
            collate pt_pt
    );
    alter table table_with_collated_field add constraint f01_check check( field_01 >= 'c' );

    show domain domain_with_collate_clause;
    show table table_with_collated_field;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DOMAIN_WITH_COLLATE_CLAUSE      CHAR(1) CHARACTER SET ISO8859_1 Nullable
    default 'v'
    check(value >='a' and value <='z')
    COLLATE ES_ES
    FIELD_01                        (DOMAIN_WITH_COLLATE_CLAUSE) CHAR(1) CHARACTER SET ISO8859_1 Nullable default 'w'
    check(value >='a' and value <='z')
    COLLATE PT_PT
    CONSTRAINT F01_CHECK:
    check( field_01 >= 'c' )
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

