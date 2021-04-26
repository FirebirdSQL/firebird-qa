#coding:utf-8
#
# id:           bugs.core_2420
# title:        Parsing error in EXECUTE STATEMENT with named parameters
# decription:   
# tracker_id:   CORE-2420
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """recreate table sch (cod int, num int, name int, prevcod int, udl char(1), root int);
set term ^;
create or alter procedure getschdet(cod int, datedoc date, datedoc2 date,
       p1 int, p2 int, p3 int, p4 int, p5 int, p6 int,
       p7 int, p8 int, p9 int, p10 int, p11 int, p12 int, p13 int)
  returns (summa int)
as
begin
  suspend;
end ^
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  c.execute("""execute block as
#  declare datedoc date;
#  declare cod int;
#  declare num int;
#  declare name int;
#  declare summa int;
#  begin
#   for execute statement (
#       ' select s.cod,s.num, s.name,sum(g.summa) from sch s
#                left join getschdet(s.cod,:datedoc ,:datedoc,0,0,0,0,0,0,0,0,0,0,0,1,3) g on 1=1
#          where s.num in (''50'',''51'') and s.udl<>''У'' and s.root=1
#           and not exists (select s2.cod from sch s2 where s2.prevcod=s.cod)
#         group by 1,2,3') (datedoc := :datedoc)
#    into :cod, :num, :name, :summa
#    do exit;
#  end""")
#  print ('Execution OK')
#  
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Execution OK
"""

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_core_2420_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


