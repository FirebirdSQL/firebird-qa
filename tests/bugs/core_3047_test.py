#coding:utf-8
#
# id:           bugs.core_3047
# title:        Wrong logic is used to resolve EXECUTE BLOCK parameters collations
# decription:
# tracker_id:   CORE-3047
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- In 2.5 (checked on WI-V2.5.5.26861):
    -- Statement failed, SQLSTATE = HY004
    -- Dynamic SQL Error
    -- -SQL error code = -204
    -- -Data type unknown
    -- -COLLATION WIN_PTBR for CHARACTER SET UTF8 is not defined
    -- (See ticket issue: "WIN_PTBR is tried to be resolved agains database charset instead of client charset: incorrect")
    -- In 3.0.0.31827 (WI- and LI-) works fine:
    -- [pcisar] 20.10.2021
    -- It fails as well in 3.0.7 and 4.0 on Linux (opensuse tumbleweed) and Windows (8.1)
    -- It appears that this test is bogus from the beginning
    set term ^;
    execute block returns (c varchar(10) collate win_ptbr) as
    begin
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    pytest.xfail("Either not fixed or wrong test")
    act_1.execute()

