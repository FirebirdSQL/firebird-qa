#coding:utf-8

"""
ID:          issue-2710-5943
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/2710
TITLE:       Records left in RDB$PAGES after rollback of CREATE TABLE statement
DESCRIPTION:
JIRA:        CORE-2284
NOTES:
    [05.03.2026] pzotov
    See also: https://github.com/FirebirdSQL/firebird/issues/5943 (CORE-5677)
    Adjusted expected output which has changed since #b38046e1 ('Encapsulation of metadata cache'; 24-feb-2026 17:31:04 +0000).
    Checked on 6.0.0.1807-46797ab.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set autoddl off;
    recreate table test_cs__master (
        str_pk varchar(32) character set UTF8 not null,
        primary key (str_pk) using index test_s_master_pk
    );

    recreate table test_cs__detail (
        str_pk varchar(32) character set WIN1251 not null,
        foreign key (str_pk) references test_cs__master (str_pk)
    );

    commit; -- this will raise: "SQLSTATE = 42000 / -partner index segment no 1 has incompatible data type"

    rollback;

    set list on;

    select count(*)
    from rdb$pages
    where rdb$relation_id >= (select rdb$relation_id from rdb$database);

    rollback;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.version('>=3.0.3')
def test_1(act: Action):

    expected_stdout_5x = """
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -partner index segment no 1 has incompatible data type
        COUNT 0
    """

    expected_stdout_6x = """
        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -RECREATE TABLE "PUBLIC"."TEST_CS__DETAIL" failed
        -partner index segment no 1 has incompatible data type
        COUNT 0
    """
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
