#coding:utf-8
#
# id:           bugs.core_3233
# title:        LIKE, STARTING and CONTAINING fail if second operand >= 32K
# decription:
# tracker_id:   CORE-3233
# min_versions: ['2.1.5']
# versions:     2.1.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.5
# resources: None

substitutions_1 = []

init_script_1 = """create table blobz (zin blob sub_type 1);
insert into blobz (zin) values ('woord');
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select 1 from blobz where zin like cast(cast('woord' as char(32766)) as blob sub_type 1) || '!' or zin='woord';
select 1 from blobz where zin like cast(cast('woord' as char(32767)) as blob sub_type 1) || '!' or zin='woord';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:\\fbtestnew\\tmp\\bugs.core_3233.fdb, User: SYSDBA
SQL>
    CONSTANT
============
           1

SQL>
    CONSTANT
============
           1

SQL>"""

@pytest.mark.version('>=2.1.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

