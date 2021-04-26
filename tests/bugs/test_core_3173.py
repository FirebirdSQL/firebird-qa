#coding:utf-8
#
# id:           bugs.core_3173
# title:        Empty result when select from SP that contains two CTE (second of them with GROUP BY clause) and INNER join
# decription:   
# tracker_id:   CORE-3173
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """
    create or alter procedure sp_main as begin end;
    create or alter procedure sp_aux1 as begin end;
    commit;
    
    recreate table zzz_tbl (
        id integer,
        company_id integer,
        hire_date date
    );
    insert into zzz_tbl (id, company_id, hire_date)
    values (123456, 654321, '01.10.2004');
    commit;
    
    set term ^;
    create or alter procedure sp_aux1 returns (val integer)
    as begin
      val=1;
      suspend;
    end
    ^
    commit ^
    
    create or alter procedure sp_main (
        COMPANY_ID integer,
        A_MONTH_BEG date)
    returns (
        PERSON_ID integer)
    AS
    begin
        for
            with
            inp as(
              select
                 company_id
                ,dateadd(1 month to p1)-1 p2
              from(
               select
                  :company_id company_id,:a_month_beg p1
                  --654321 company_id,cast('01.09.2010' as date) p1
                from
                --rdb$database
                sp_aux1
              )t
            )
            
            ,person_nfo as
            (
            select n.id person_id,i.p2
            --from inp i join zzz_tbl n on n.company_id = i.company_id
            from zzz_tbl n left join inp i on n.company_id = i.company_id
            group by n.id,p2
            )
            
            select f.person_id
            from person_nfo f
            join zzz_tbl nt on nt.hire_date <= f.p2
        into :person_id
        do suspend;
    end
    
    ^ set term ;^
    commit;

  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select * from sp_main(654321, '01.09.2010');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PERSON_ID                       123456
  """

@pytest.mark.version('>=2.5.1')
def test_core_3173_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

