#coding:utf-8
#
# id:           bugs.core_1997
# title:        Broken foreign key handling for multi-segmented index using multi-level collations
# decription:   
# tracker_id:   CORE-1997
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """create table pk (
    c1 varchar (5) character set utf8 collate unicode_ci,
    c2 varchar (5) character set utf8 collate unicode_ci,
    primary key (c1, c2)
);
commit;
create table fk (
    c1 varchar (5) character set utf8 collate unicode_ci,
    c2 varchar (5) character set utf8 collate unicode_ci,
    foreign key (c1, c2) references pk
);
commit;
insert into pk values ('a', 'b');
insert into fk values ('A', 'b');
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """delete from pk; -- should not be allowed
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """Statement failed, SQLSTATE = 23000
violation of FOREIGN KEY constraint "INTEG_2" on table "FK"
-Foreign key references are present for the record
-Problematic key value is ("C1" = 'a', "C2" = 'b')
"""

@pytest.mark.version('>=2.5.2')
def test_core_1997_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

