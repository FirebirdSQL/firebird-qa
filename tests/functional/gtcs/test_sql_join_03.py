#coding:utf-8
#
# id:           functional.gtcs.sql_join_03
# title:        GTCS/tests/C_SQL_JOIN_3. Ability to run query: ( A LEFT JOIN B ) INER JOIN C, plus ORDER BY with fields not from SELECT list.
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/C_SQL_JOIN_3.script 
#                   Original backup file that is used for this test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/test-files/atlas.gbk 
#                   Checked on 4.0.0.1896; 3.0.6.33288; 2.5.9.27149
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(from_backup='gtcs_atlas.fbk', init=init_script_1)

test_script_1 = """

    select 'DSQL-test' as msg, b.team_name, c.city, s.state_name
    from (
        cities c left join states s on s.state = c.state
    )
    inner join baseball_teams b on b.city = c.city
    --order by b.team_name, c.city, s.state_name;
    order by b.home_stadium, c.population, s.capital;

    set term ^;
    execute block returns(
         msg varchar(10)
        ,team_name type of column baseball_teams.team_name
        ,city type of column cities.city
        ,state_name type of column states.state_name
    ) as
        declare c cursor for (
            select 'PSQL-test' as msg, b.team_name, c.city, s.state_name
            from (
                cities c left join states s on s.state = c.state
            )
            inner join baseball_teams b on b.city = c.city
            --order by b.team_name, c.city, s.state_name
            order by b.home_stadium, c.population, s.capital
        );
    begin
        open c;
        while (1=1) do
        begin
            fetch c into msg, team_name, city, state_name;
            if (row_count = 0) then
                leave;
            suspend;
        end
        close c;
    end
    ^
    set term ;^

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG       TEAM_NAME       CITY                      STATE_NAME
    DSQL-test Astros          Houston                   Texas
    DSQL-test Braves          Atlanta                   Georgia
    DSQL-test Cardinals       St. Louis                 Missouri
    DSQL-test Giants          San Francisco             California
    DSQL-test Indians         Cleveland                 Ohio
    DSQL-test White Sox       Chicago                   Illinois
    DSQL-test Dodgers         Los Angeles               California
    DSQL-test Red Sox         Boston                    Massachusetts
    DSQL-test Mariners        Seattle                   Washington
    DSQL-test Brewers         Milwaukee                 Wisconsin
    DSQL-test Royals          Kansas City               Missouri
    DSQL-test Padres          San Diego                 California
    DSQL-test Mets            New York                  New York
    DSQL-test Pirates         Pittsburgh                Pennsylvania
    DSQL-test Tigers          Detroit                   Michigan
    DSQL-test Phillies        Philadelphia              Pennsylvania
    DSQL-test Cubs            Chicago                   Illinois
    DSQL-test Yankees         New York                  New York

    MSG        TEAM_NAME       CITY                      STATE_NAME
    PSQL-test  Astros          Houston                   Texas
    PSQL-test  Braves          Atlanta                   Georgia
    PSQL-test  Cardinals       St. Louis                 Missouri
    PSQL-test  Giants          San Francisco             California
    PSQL-test  Indians         Cleveland                 Ohio
    PSQL-test  White Sox       Chicago                   Illinois
    PSQL-test  Dodgers         Los Angeles               California
    PSQL-test  Red Sox         Boston                    Massachusetts
    PSQL-test  Mariners        Seattle                   Washington
    PSQL-test  Brewers         Milwaukee                 Wisconsin
    PSQL-test  Royals          Kansas City               Missouri
    PSQL-test  Padres          San Diego                 California
    PSQL-test  Mets            New York                  New York
    PSQL-test  Pirates         Pittsburgh                Pennsylvania
    PSQL-test  Tigers          Detroit                   Michigan
    PSQL-test  Phillies        Philadelphia              Pennsylvania
    PSQL-test  Cubs            Chicago                   Illinois
    PSQL-test  Yankees         New York                  New York
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

