#coding:utf-8
#
# id:           bugs.gh_7034
# title:        Scroll cursor server crash
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/7034
#               
#                   Confirmed bug (crash) on 5.0.0.279, 4.0.1.2649, 3.0.8.33525.
#                   Checked on intermediate snapshots: 5.0.0.292; 4.0.1.2650; 3.0.8.33527 -- all OK.
#                
# tracker_id:   
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^ ;
    create table ca (
        f1 integer,
        f2 integer
    )^

    		commit^

    insert into ca (f1, f2) values (1, 3)^
    insert into ca (f1, f2) values (2, 3)^
    insert into ca (f1, f2) values (2, 4)^
    insert into ca (f1, f2) values (2, 3)^
    commit^

    create or alter procedure gt( privilegy integer)
    returns ( result integer) as
    begin
        result=0;
        suspend;
    end^

    		commit^

    create or alter view psa(result) as
    select (select result from gt(36)) from rdb$database
    ^

    		commit^

    create or alter view vca(f1, f2) as
    select c.* from psa pca
    inner join ca c on pca.result=0
    where pca.result=0
    ^

    		commit^

    set heading off ^

    execute block returns (aid integer) as
        declare bdate type of column ca.f1;
        declare edate type of column ca.f1;
        declare da scroll cursor for
        (
            select ca.id from
            (
                select distinct sacc.f2 id from
                vca sacc
                where 1=1 and f1 between :bdate and :edate
            ) ca
            order by 1
        );
    begin
        select min(f1) from vca into :bdate;
        select max(f1) from vca into :edate;
        open da;
        fetch first from da into :aid; --crash
        suspend;
    end
    ^

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    3
"""

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
