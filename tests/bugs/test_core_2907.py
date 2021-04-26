#coding:utf-8
#
# id:           bugs.core_2907
# title:        Unable to catch exceptions that are thrown inside a dynamic builded execute block.
# decription:   
# tracker_id:   CORE-2907
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE OR ALTER EXCEPTION EX_TEST 'test';

SET TERM ^ ;
CREATE OR ALTER procedure sp_1
as
declare variable v_stmt varchar(256);
begin

  v_stmt = 'execute block as '||
           'begin '||
           ' exception ex_test; '||
           'end';
  execute statement v_stmt;

end
^
SET TERM ; ^



SET TERM ^ ;
CREATE OR ALTER procedure sp_2
as
begin
  begin
    execute procedure sp_1;

    when exception ex_test do
    begin
      exit;
    end
  end
end
^
SET TERM ; ^

SET TERM ^ ;
CREATE OR ALTER procedure sp_3
as
begin
  begin
    execute procedure sp_1;
    when any do
    begin
      exit;
    end
  end
end
^
SET TERM ; ^
commit;

"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """EXECUTE PROCEDURE SP_2;
EXECUTE PROCEDURE SP_3;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_core_2907_1(act_1: Action):
    act_1.execute()

