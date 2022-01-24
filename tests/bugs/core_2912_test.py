#coding:utf-8

"""
ID:          issue-3296
ISSUE:       3296
TITLE:       Exception when upper casing string with lowercase y trema (code 0xFF in ISO8859_1)
DESCRIPTION:
  Test creates table and fills it with non-ascii characters in init_script, using charset = UTF8.
  Then it generates .sql script for running it in separae ISQL process.
  This script makes connection to test DB using charset = ISO8859_1 and perform several queries.
  Result will be redirected to .log and .err files (they will be encoded, of course, also in ISO8859_1).
  Finally, we open .log file (using codecs package), convert its content to UTF8 and show in expected_stdout.
NOTES:
[16.11.2021]
  This test fails as UPPER('ÿ') does not work properly
JIRA:        CORE-2912
"""

import pytest
from firebird.qa import *

init_script = """
    create table test(c varchar(10));
    commit;
    insert into test(c) values('ÿ');
    insert into test(c) values('Faÿ');
    commit;
    create index test_cu on test computed by (upper (c collate iso8859_1));
    commit;
"""

db = db_factory(charset='ISO8859_1', init=init_script)

act = python_act('db')

test_script = """set names ISO8859_1;
    set list on;
    select upper('aÿb') au from rdb$database;
    select c, upper(c) cu from test where c starting with upper('ÿ');
    select c, upper(c) cu from test where c containing 'Faÿ';
    select c, upper(c) cu from test where c starting with 'Faÿ';
    select c, upper(c) cu from test where c like 'Faÿ%';
    -- ### ACHTUNG ###
    -- As of WI-V2.5.4.26857, following will FAILS if character class "alpha"
    -- will be specified not in UPPER case (see note in CORE-4740  08/Apr/15 05:48 PM):
    select c, upper(c) cu from test where c similar to '[[:ALPHA:]]{1,}ÿ%';
    set plan on;
    select c from test where upper (c collate iso8859_1) =  upper('ÿ');
    select c, upper(c) cu from test where upper (c collate iso8859_1) starting with upper('Faÿ');
"""

expected_stdout = """
    AU                              AÿB
    C                               ÿ
    CU                              ÿ
    C                               Faÿ
    CU                              FAÿ
    C                               Faÿ
    CU                              FAÿ
    C                               Faÿ
    CU                              FAÿ
    C                               Faÿ
    CU                              FAÿ
    PLAN (TEST INDEX (TEST_CU))
    C                               ÿ
    PLAN (TEST INDEX (TEST_CU))
    C                               Faÿ
    CU                              FAÿ
"""

@pytest.mark.skip("FIXME: see notes")
@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], charset='ISO8859_1', input=test_script)
    assert act.clean_stdout == act.clean_expected_stdout
