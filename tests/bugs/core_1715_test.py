#coding:utf-8
#
# id:           bugs.core_1715
# title:        Incorrect "key size exceeds implementation restriction for index" error
# decription:   
# tracker_id:   CORE-1715
# min_versions: []
# versions:     2.1.0
# qmid:         bugs.core_1715

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (
   t1_id integer not null
   , vc_50_utf8_utf8 varchar(253) character set utf8 collate utf8
   , vc_50_utf8_unicode varchar(169) character set utf8 collate unicode
   , constraint pk_t1_id primary key (t1_id)
);"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """create index i_vc_50_utf8_unicode on t1 (vc_50_utf8_unicode);
create index i_vc_50_utf8_utf8 on t1 (vc_50_utf8_utf8);
commit;
show index;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """I_VC_50_UTF8_UNICODE INDEX ON T1(VC_50_UTF8_UNICODE)
I_VC_50_UTF8_UTF8 INDEX ON T1(VC_50_UTF8_UTF8)
PK_T1_ID UNIQUE INDEX ON T1(T1_ID)
"""

@pytest.mark.version('>=2.1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

