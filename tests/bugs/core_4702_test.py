#coding:utf-8

"""
ID:          issue-5010
ISSUE:       5010
TITLE:       Regression: Join order in v3 is less optimal than in v2.x
DESCRIPTION:
JIRA:        CORE-4702
FBTEST:      bugs.core_4702
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table trial_line (
        code_trial_line integer not null,
        code_trial integer not null
    );

    recreate table trial (
        code_trial integer not null,
        code_prize integer not null,
        bydate date
    );


    recreate table prize (
        code_prize integer not null,
        name varchar(70) not null
    );
    commit;


    insert into prize(code_prize, name)
    with recursive t (n) as (
      select 1 from rdb$database
      union all
      select n+1 from t where n < 1000
    )
    select n+8000, '' from t;
    commit;

    insert into trial(code_trial, code_prize, bydate)
    with recursive t (n) as (
      select 1 from rdb$database
      union all
      select n+1 from t where n < 1000
    )
    select t1.n + (t2.n-1)*1000, mod(t1.n, 20)+8001, dateadd(t1.n day to date '01.01.2000')
    from t t1, t t2
    where t1.n + (t2.n-1)*1000 < 100000;
    commit;

    insert into trial_line(code_trial_line, code_trial)
    with recursive t (n) as (
      select 1 from rdb$database
      union all
      select n+1 from t where n < 1000
    )
    select t1.n + (t2.n-1)*1000, mod(t1.n + (t2.n-1)*1000, 99998)+1
    from t t1, t t2
    where t1.n + (t2.n-1)*1000 < 150000;
    commit;

    alter table trial add constraint pk_trial primary key (code_trial);
    alter table prize add constraint pk_prize primary key (code_prize);
    alter table trial_line add constraint pk_trial_line primary key (code_trial_line);

    alter table trial_line add constraint fk_trial_line_trial foreign key (code_trial) references trial (code_trial);
    alter table trial add constraint fk_trial_prize foreign key (code_prize) references prize (code_prize);

    create index idx_bydate on trial(bydate);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set planonly;
    select count(*)
    from
       trial
       join prize on prize.code_prize = trial.code_prize
       join trial_line on trial_line.code_trial = trial.code_trial
    where trial.bydate between date '01.01.2000' and date '31.12.2000';
    -- Confirmed ineffective plan in WI-T3.0.0.31374 Firebird 3.0 Beta 1:
    -- PLAN JOIN (TRIAL INDEX (IDX_BYDATE), TRIAL_LINE INDEX (FK_TRIAL_LINE_TRIAL), PRIZE INDEX (PK_PRIZE))
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN JOIN (TRIAL INDEX (IDX_BYDATE), PRIZE INDEX (PK_PRIZE), TRIAL_LINE INDEX (FK_TRIAL_LINE_TRIAL))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

