#coding:utf-8

"""
ID:          intfunc.misc.gen_uuid
TITLE:       GEN_UUID()
DESCRIPTION: Returns a universal unique number.
FBTEST:      functional.intfunc.misc.gen_uuid_01
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
create table test( id char(30) );

--on verrifie qu'il y en a pas deux identique
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );
insert into test values(CAST(GEN_UUID() AS VARCHAR(255)) );


select count(id)  from test group by id;"""

act = isql_act('db', test_script)

expected_stdout = """
COUNT
=====================
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
