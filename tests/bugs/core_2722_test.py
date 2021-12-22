#coding:utf-8
#
# id:           bugs.core_2722
# title:        Storage of malformed blob is allowed when copying from a blob with NONE/OCTETS charset
# decription:   
# tracker_id:   CORE-2722
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """create table t (b1 blob sub_type text, b2 blob sub_type text character set utf8);

"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """-- This is correct and raise "Malformed string" error
insert into t (b2) values (x'F0');

insert into t (b1) values (x'F0');

-- This should raise second "Malformed string" error
update t set b2 = b1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 22000
Malformed string
Statement failed, SQLSTATE = 22000
Malformed string
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

