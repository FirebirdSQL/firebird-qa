#coding:utf-8

"""
ID:          gtcs.isql-show-command-collation
TITLE:       Misplaced collation when extracting metadata with isql
DESCRIPTION:
  ::: NB :::
  ### Name of original test has no any relation with actual task of this test: ###
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_20.script

  bug #223126 Misplaced collation when extracting metadata with isql
FBTEST:      functional.gtcs.isql_show_command_collation
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script, substitutions=[('[ \t]+', ' ')])

expected_stdout = """
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

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
