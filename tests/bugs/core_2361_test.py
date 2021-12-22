#coding:utf-8
#
# id:           bugs.core_2361
# title:        String truncation reading 8859-1 Spanish column using isc_dsql_fetch with UTF-8 connection..
# decription:   
# tracker_id:   CORE-2361
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table "'Master by Reseller$'" (
    "Tier" VARCHAR(20) CHARACTER SET ISO8859_1 COLLATE ES_ES_CI_AI
);

commit;

insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('(blank)');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('Approved');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('Bronze');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('DMR');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('Domestic Distributor');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('End-User');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('Evaluation');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('Gold');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('New');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('Silver');
insert into "'Master by Reseller$'" ( "Tier" ) VALUES ('VAM');

commit;
"""

db_1 = db_factory(page_size=4096, charset='ISO8859_1', sql_dialect=3, init=init_script_1)

test_script_1 = """select case when 1 = 0 then '(blank)' else "'Master by Reseller$'"."Tier" end from "'Master by Reseller$'";
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
CASE
====================
(blank)
Approved
Bronze
DMR
Domestic Distributor
End-User
Evaluation
Gold
New
Silver
VAM

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

