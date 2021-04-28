#coding:utf-8
#
# id:           bugs.core_2579
# title:        Parameters and variables cannot be used as expressions in EXECUTE PROCEDURE parameters without a colon prefix
# decription:   
# tracker_id:   CORE-2579
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^ ;

create procedure P123 (param int)
as
begin
   execute procedure p123 (param);
end ^

set term ; ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.execute()

