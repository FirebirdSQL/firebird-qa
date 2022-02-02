#coding:utf-8

"""
ID:          issue-5349
ISSUE:       5349
TITLE:       CHAR_TO_UUID on column with index throws expression evaluation not supported
  Human readable UUID argument for CHAR_TO_UUID must be of exact length 36
DESCRIPTION:
JIRA:        CORE-5062
FBTEST:      bugs.core_5062
"""

import pytest
from firebird.qa import *

init_script = """
recreate table test_uuid(
    datavalue int,
    uuid char(16) character set octets,
    constraint test_uuid_unq unique(uuid)
);
commit;
insert into test_uuid(datavalue, uuid) values( 1, char_to_uuid('57F2B8C7-E1D8-4B61-9086-C66D1794F2D9') );
--insert into test_uuid(datavalue, uuid) values( 2, char_to_uuid('37F2B8C3-E1D8-4B31-9083-C33D1794F2D3') );
commit;
"""

db = db_factory(init=init_script)

act = python_act('db')

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    with act.db.connect() as con:
        c = con.cursor()
        stmt = c.prepare("select datavalue from test_uuid where uuid = char_to_uuid(?)")
        assert stmt.plan == 'PLAN (TEST_UUID INDEX (TEST_UUID_UNQ))'
        result = c.execute(stmt, ['57F2B8C7-E1D8-4B61-9086-C66D1794F2D9']).fetchall()
        assert result == [(1, )]

