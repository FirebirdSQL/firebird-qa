#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9059
TITLE:       Weird violation of FOREIGN KEY for [var]binary datatype when PK and FK indices have opposite direction
DESCRIPTION:
NOTES:
    [17.06.2026] pzotov
    Confirmed bug on 6.0.0.2002; 5.0.5.1833; 4.0.8.3285; 3.0.15.33863.
    Checked on 6.0.0.2012; 5.0.5.1837; 4.0.8.3286; 3.0.15.33867.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(f01 varchar(16) character set octets not null, f02 varchar(16) character set octets);
    set term ^;
    execute block as
        declare n int = 20000;
    begin
        while ( n > 0 ) do
        begin
            insert into test(f01) values(gen_uuid());
            n = n - 1;
        end
    end
    ^
    set term ;^
    update test set f02 = f01;
    commit;

    alter table test add constraint test_f01_pkey primary key(f01)
    ;
    alter table test add constraint test_f02_fkey foreign key(f02) references test(f01)
    using descending index test_f02_fk_desc
    ;
    --------------------------------------------------
    alter table test drop constraint test_f02_fkey;
    alter table test drop constraint test_f01_pkey;
    --------------------------------------------------
    alter table test add constraint test_f01_pkey primary key(f01)
    using descending index test_f01_pk_desc
    ;
    alter table test add constraint test_f02_fkey foreign key(f02) references test(f01)
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
"""

@pytest.mark.version('>=3.0.15')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

