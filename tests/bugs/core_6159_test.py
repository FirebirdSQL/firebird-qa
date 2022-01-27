#coding:utf-8

"""
ID:          issue-6408
ISSUE:       6408
TITLE:       SUBSTRING SIMILAR is described with wrong data type in DSQL
DESCRIPTION:
JIRA:        CORE-6159
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(id int, s varchar(1000), b blob);
    insert into test(id, s,b) values( 1, 'charchar', 'fooobaar' );
    insert into test(id, s,b) values( 2, 'fooobaar', 'blobblob' );
    commit;

    set list on;
    set blob on;
    set sqlda_display on;
    set count on;
    select x from (select substring( s similar 'c#"harc#"har' escape '#') x from test ) where x is not null;
    select x from (select substring( b similar 'b#"lobb#"lob' escape '#') x from test ) where x is not null;

"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype|harc|lobb|affected).)*$', ''),
                                                 ('[ \t]+', ' '), ('Nullable.*', 'Nullable')])

expected_stdout = """
    01: sqltype: 448 VARYING Nullable
    X harc
    Records affected: 1

    01: sqltype: 520 BLOB Nullable
    lobb
    Records affected: 1
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
