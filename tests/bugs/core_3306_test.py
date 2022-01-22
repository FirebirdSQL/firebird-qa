#coding:utf-8

"""
ID:          issue-3673
ISSUE:       3673
TITLE:       Invariant sub-query is treated as variant thus causing multiple invokations of a nested stored procedure
DESCRIPTION:
JIRA:        CORE-3306
"""

import pytest
from firebird.qa import *

init_script = """SET TERM !!;
Create Table tt_table(Field1 varchar(100))!!
Create Or Alter PROCEDURE SPR_TEST (pName Varchar(2000)) RETURNS (sValue Varchar(255)) AS
BEGIN
  Insert Into tt_table(field1) values(:pName);
  sValue=:pName;
  suspend;
End!!
COMMIT!!
SET TERM ;!!
Select count(*)
from rdb$types
where rdb$field_name like (select sValue From spr_test('SIMSIM'));
COMMIT;"""

db = db_factory(init=init_script)

act = isql_act('db', "select count(*) from tt_table;")

expected_stdout = """
                COUNT
=====================
                    1

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

