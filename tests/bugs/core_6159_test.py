#coding:utf-8
#
# id:           bugs.core_6159
# title:        SUBSTRING SIMILAR is described with wrong data type in DSQL
# decription:   
#                   Confirmed correct work on 4.0.0.1627.
#                   FB 3.x and 4.0.0.1535 raises exception after select substring(blob_field similar <pattern> ) from ...:
#                       Statement failed, SQLSTATE = 42000
#                       Invalid SIMILAR TO pattern
#                
# tracker_id:   CORE-6159
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!sqltype|harc|lobb|affected).)*$', ''), ('[ \t]+', ' '), ('Nullable.*', 'Nullable')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 448 VARYING Nullable
    X harc
    Records affected: 1

    01: sqltype: 520 BLOB Nullable
    lobb
    Records affected: 1
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

