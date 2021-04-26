#coding:utf-8
#
# id:           functional.trigger.database.transactioncommit_01
# title:        Trigger on commit transaction. See also CORE-645
# decription:   Test trigger on commit transaction
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
	SET AUTODDL OFF;
	CREATE TABLE T1
	(
		T1_ID BIGINT NOT NULL,
		T1_VAL CHAR(10) ,
		CONSTRAINT PK_T1 PRIMARY KEY (T1_ID)
	);

	CREATE SEQUENCE S_TRANSACTION;

	SET TERM ^ ;
	RECREATE TRIGGER TRIG_TRANSAC ACTIVE
	ON TRANSACTION COMMIT
	POSITION 0
	AS
	BEGIN
		RDB$SET_CONTEXT('USER_SESSION', 'Trn_ID', (NEXT VALUE FOR S_TRANSACTION));
	 END^

	SET TERM ; ^

	COMMIT;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET AUTODDL OFF;
    
	SET LIST ON;
	
	INSERT INTO T1 VALUES (1,'val1');
	SELECT RDB$GET_CONTEXT('USER_SESSION', 'Trn_ID') AS CTX_VAR FROM RDB$DATABASE;
	COMMIT;
	UPDATE T1 SET T1_VAL='val1mod' WHERE T1_ID=1;
	SELECT RDB$GET_CONTEXT('USER_SESSION', 'Trn_ID') AS CTX_VAR  FROM RDB$DATABASE;
	ROLLBACK;
	DELETE FROM T1 WHERE T1_ID=1;
	SELECT RDB$GET_CONTEXT('USER_SESSION', 'Trn_ID') AS CTX_VAR  FROM RDB$DATABASE;
	COMMIT;
	SELECT RDB$GET_CONTEXT('USER_SESSION', 'Trn_ID') AS CTX_VAR  FROM RDB$DATABASE;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	CTX_VAR                         <null>
	CTX_VAR                         3
	CTX_VAR                         3
	CTX_VAR                         4  
  """

@pytest.mark.version('>=2.1')
def test_transactioncommit_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

