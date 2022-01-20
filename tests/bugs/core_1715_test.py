#coding:utf-8

"""
ID:          issue-2140
ISSUE:       2140
TITLE:       Incorrect "key size exceeds implementation restriction for index" error
DESCRIPTION:
JIRA:        CORE-1715
"""

import pytest
from firebird.qa import *

init_script = """create table t1 (
   t1_id integer not null
   , vc_50_utf8_utf8 varchar(253) character set utf8 collate utf8
   , vc_50_utf8_unicode varchar(169) character set utf8 collate unicode
   , constraint pk_t1_id primary key (t1_id)
);"""

db = db_factory(charset='UTF8', init=init_script)

test_script = """create index i_vc_50_utf8_unicode on t1 (vc_50_utf8_unicode);
create index i_vc_50_utf8_utf8 on t1 (vc_50_utf8_utf8);
commit;
show index;
"""

act = isql_act('db', test_script)

expected_stdout = """I_VC_50_UTF8_UNICODE INDEX ON T1(VC_50_UTF8_UNICODE)
I_VC_50_UTF8_UTF8 INDEX ON T1(VC_50_UTF8_UTF8)
PK_T1_ID UNIQUE INDEX ON T1(T1_ID)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

