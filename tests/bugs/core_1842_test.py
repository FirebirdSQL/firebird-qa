#coding:utf-8
#
# id:           bugs.core_1842
# title:        DEFAULT values are unnecessary evaluated
# decription:   
# tracker_id:   CORE-1842
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table tb_date (
    tb_date_id integer not null primary key,
    f_date date default 0);
commit;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """INSERT INTO TB_DATE (
    TB_DATE_ID, F_DATE)
  VALUES (
    1, '09-MAY-1945');
insert into tb_date (
    tb_date_id, f_date)
  values (
    2, null);
commit;
SELECT TB_DATE_ID, F_DATE FROM TB_DATE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_1842.fdb, User: SYSDBA
SQL> CON> CON> CON> SQL> CON> CON> CON> SQL> SQL>
  TB_DATE_ID      F_DATE
============ ===========
           1 1945-05-09
           2      <null>

SQL>"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

