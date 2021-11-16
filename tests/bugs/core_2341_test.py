#coding:utf-8
#
# id:           bugs.core_2341
# title:        Hidden variables conflict with output parameters, causing assertions, unexpected errors or possibly incorrect results
# decription:
# tracker_id:   CORE-2341
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#
#  cmd = c.prep("""execute block (i varchar(10) = ?) returns (o varchar(10))
#  as
#  begin
#    o = coalesce(cast(o as date), current_date);
#    o = i;
#    suspend;
#  end""")
#  c.execute(cmd,['asd'])
#  printData(c)
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """O
----------
asd
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action, capsys):
    with act_1.db.connect() as con:
        c = con.cursor()
        cmd = c.prepare("""execute block (i varchar(10) = ?) returns (o varchar(10))
        as
        begin
          o = coalesce(cast(o as date), current_date);
          o = i;
          suspend;
        end""")
        c.execute(cmd, ['asd'])
        act_1.print_data(c)
        #
        act_1.expected_stdout = expected_stdout_1
        act_1.stdout = capsys.readouterr().out
        assert act_1.clean_stdout == act_1.clean_expected_stdout


