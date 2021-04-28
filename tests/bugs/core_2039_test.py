#coding:utf-8
#
# id:           bugs.core_2039
# title:        Domain-level CHECK constraints wrongly process NULL values
# decription:   
# tracker_id:   CORE-2039
# min_versions: []
# versions:     2.1.2
# qmid:         bugs.core_2039

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.2
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN D_DATE AS DATE
CHECK (VALUE BETWEEN DATE '01.01.1900' AND DATE '01.01.2050');

CREATE PROCEDURE TMP (PDATE D_DATE)
AS BEGIN END;

COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """EXECUTE PROCEDURE TMP (NULL);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1.2')
def test_1(act_1: Action):
    act_1.execute()

