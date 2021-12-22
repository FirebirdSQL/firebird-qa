#coding:utf-8
#
# id:           functional.trigger.alter.09
# title:        ALTER TRIGGER - POSITION
# decription:   ALTER TRIGGER - POSITION
#               Test by checking trigger seqeunce
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
#               CREATE TRIGGER
#               INSERT
#               Basic SELECT
# tracker_id:   
# min_versions: []
# versions:     1.0
# qmid:         functional.trigger.alter.alter_trigger_09

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE test( id INTEGER NOT NULL CONSTRAINT unq UNIQUE,
                   text VARCHAR(32));
SET TERM ^;
CREATE TRIGGER tg1 FOR test BEFORE INSERT POSITION 1
AS
BEGIN
  new.text=new.text||'tg1 ';
END ^

CREATE TRIGGER tg2 FOR test BEFORE INSERT POSITION 10
AS
BEGIN
  new.text=new.text||'tg2 ';
END ^
SET TERM ;^
commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """ALTER TRIGGER tg2 POSITION 0;
INSERT INTO test VALUES(0,'');
COMMIT;
SELECT text FROM test;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """TEXT
================================

tg2 tg1"""

@pytest.mark.version('>=1.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

