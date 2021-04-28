#coding:utf-8
#
# id:           functional.intfunc.misc.decode_01
# title:        test de la fonction decode
# decription:   decode is a shortcut for a case when else expreession.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.intfunc.misc.decode_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET ECHO OFF;
CREATE  TABLE TMPTEST( id INTEGER );

insert into TMPTEST(id)
values(1);
insert into TMPTEST(id)
values(2);
insert into TMPTEST(id)
values(3);
insert into TMPTEST(id)
values(4);
insert into TMPTEST(id)
values(5);

-- count doit etre egal a 0 dans ce cas
select decode(id,1,'un',2,'deux',3,'trois','plus grand') from TMPTEST;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """DECODE
==========
un
deux
trois
plus grand
plus grand

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

