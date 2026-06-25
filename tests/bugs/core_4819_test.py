#coding:utf-8

"""
ID:          issue-5116
ISSUE:       5116
TITLE:       EXECUTE PROCEDURE's RETURNING_VALUES and EXECUTE STATEMENT's INTO does not check validity of assignments targets leading to bugcheck
DESCRIPTION:
JIRA:        CORE-4819
FBTEST:      bugs.core_4819
NOTES:
    [26.06.2026] pzotov
    1. Confirmed bug on 3.0.0.31828 but current version of firebird-driver can not be used for such check (AV raises).
       ISQL displays EB with 'execute procedure sp_test(c1.x) returning_values(c1.y)' hangs; firebird.log contains:
       "internal Firebird consistency check (EVL_assign_to: invalid operation (229), file: evl.cpp line: 205)"
       ISQL process must be killed using external tools (e.g. taskkill etc) because Ctrl-C or Ctrl-Brk have no effect.
    2. Previous version of this test started to fail since 6.0.0.1771-f73321c (i.e. when shared metadata cache was introduced).
       Investigation unexpectedly revealed BUG that did exist in all major versions since 3.x, namely: binary representation
       of AIUD-trigger that could *not* be compiled remained in metadata cache and prevented further DML actions with a table
       (error "SQLSTATE = 42000 / attempted update of read-only column" remained until RECONNECT).
       This bug was registered in the tracker:
       https://github.com/FirebirdSQL/firebird/issues/8997
       For this test it is enough only to check outcome of:
           * execute proc ... returning_values(<cursor.some_column>);
           * execute statement ('execute procedure ...') ( ... ) into <cursor.some_column>;
           * attempt to create triggers which try to change 'old.<some_column>'
       Further DML actions after such failed actions have no sense for 3.x ... 5.x because of bug.
       For 6.x separate test with similar AIUD-triggers *and* DML will be implemented.
       Discussed with FB-team, letters since 20.04.2026 1751.

    Checked on 6.0.0.2028; 5.0.5.1837; 4.0.8.3286; 3.0.15.33867
"""
import subprocess
from difflib import unified_diff
from pathlib import Path
import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    create or alter procedure sp_test(a_x int) as begin end;
    recreate table test(id int primary key, x bigint, y bigint);

    set term ^;
    create or alter procedure sp_test(a_x int) returns(o_y int) as
    begin
        o_y = 7 * a_x;
        suspend;
    end
    ^
    commit
    ^
    set term ;^

    -- ######################################################################
    -- Check-1. Check when call 'execute proc returning_values' inside implicit cursor:
    set term ^;
    execute block returns(msg varchar(20), old_y int, new_y int) as
    begin
      insert into test values(1,  3,  7);
      for
          select x, y from test
          as cursor c1
      do begin
          old_y = c1.y;

          -- WI-T3.0.0.31845. Following leads to:
          -- Statement failed, SQLSTATE = XX000
          -- internal Firebird consistency check (EVL_assign_to: invalid operation (229), file: evl.cpp line: 205)
          -- Since WI-T3.0.0.31846 must produce:
          -- Statement failed, SQLSTATE = 42000
          -- attempted update of read-only column

          execute procedure sp_test(c1.x) returning_values(c1.y);

          -- Following code must NOT execute:
          new_y = c1.y;
          msg = 'UNEXPECTED-1: old_y = ' || old_y || ', new_y = ' || new_y;
          suspend;
      end
    end
    ^
    set term ;^
    rollback;

    -- ######################################################################
    -- Check-2. Check when call 'execute statement' inside implicit cursor:
    set term ^;
    execute block returns(msg varchar(20), old_y int, new_y int) as
    begin
      msg='within cursor-2:';
      for
          select x, y from test
          as cursor c2
      do begin
          old_y = c2.y;

          -- Since WI-T3.0.0.31846 following must produce:
          -- Statement failed, SQLSTATE = 42000
          -- attempted update of read-only column
          execute statement ('execute procedure sp_test( ? )') ( c2.x ) into c2.y;

          -- Following code must NOT execute:
          new_y = c2.y;
          -- Following code must NOT execute:
          msg = 'UNEXPECTED-2: old_y = ' || old_y || ', new_y = ' || new_y;
          suspend;
      end
    end
    ^
    set term ;^
    rollback;

    -- ######################################################################
    -- Check-3. Check AIUD triggers

    set term ^;
    create or alter trigger test_aud1 for test active after insert or update or delete as
    begin
        -- Since WI-T3.0.0.31846 following must produce:
        -- Statement failed, SQLSTATE = 42000
        -- attempted update of read-only column

        if (not inserting) then
            begin
                execute procedure sp_test(old.x) returning_values(old.x);
            end
        else
            begin
                execute procedure sp_test(new.x) returning_values(new.y);
            end
    end
    ^

    create or alter trigger test_aud2 for test active after insert or update or delete as
    begin
        -- Since WI-T3.0.0.31846 following must produce:
        -- Statement failed, SQLSTATE = 42000
        -- attempted update of read-only column
        if (not inserting) then
            begin
                execute statement ('execute procedure sp_test( ? )') ( 2 * old.x ) into old.y;
            end
        else
            begin
                execute statement ('execute procedure sp_test( ? )') ( 2 * new.x ) into new.y;
            end
    end
    ^
    set term ;^
    commit;

    -- must be zero:
    select count(*) as trg_count from rdb$triggers where rdb$relation_name = upper('test');
    -- shell ping 192.0.2.2;
"""

substitutions = [('[ \t]+', ' '), ('After line \\d+.*', '')]
act = python_act('db', test_script, substitutions = substitutions)

tmp_sql = temp_file('tmp_core_4819.sql')
tmp_log = temp_file('tmp_core_4819.log')

MAX_WAIT_FOR_ISQL_STOP = 3

@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path, capsys):

    # Initial content of firebird.log:
    log_before = act.get_firebird_log()

    tmp_sql.write_text(test_script)
    rc = 0
    try:
        with open(tmp_log, 'w') as f_log:
            p = subprocess.run( [ act.vars['isql'],
                                  '-user', act.db.user,
                                  '-password', act.db.password,
                                  act.db.dsn,
                                  '-i', tmp_sql
                                ], 
                                stdout = f_log, stderr = subprocess.STDOUT,
                                timeout = MAX_WAIT_FOR_ISQL_STOP
                              )
            rc = p.returncode

    except Exception as e:
        print(f'{e.__class__=}')
        # DO NOT: print(f'{e.errno=}') AttributeError: 'TimeoutExpired' object has no attribute 'errno'
        # Command '[...]'  timed out after NNN seconds
        print(e.__str__())
        rc = -1 # need because timeout does not change returncode!

    # Get content of firebird.log AFTER test (diff must remain empty)
    log_after = act.get_firebird_log()
    fb_log_diff = list(unified_diff(log_before, log_after))
    if fb_log_diff:
        print('UNEXPECTED new lines in firbird.log:')
        for line in fb_log_diff:
            if line.startswith('+') and line[2:].strip():
                print(line.rstrip())
        
    print(f'ISQL returncode: {rc}')
    if tmp_log.is_file():
        with open(tmp_log, 'r') as f:
            for line in f:
                print(line)

    fb3x_checked_stdout = """
        ISQL returncode: 1
        Statement failed, SQLSTATE = 42000
        attempted update of read-only column

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column

        TRG_COUNT 0
    """

    fb5x_checked_stdout = """
        ISQL returncode: 1
        Statement failed, SQLSTATE = 42000
        attempted update of read-only column C1.Y

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column C2.Y

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column TEST.X

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column TEST.Y
        
        TRG_COUNT 0
    """

    fb6x_checked_stdout = """
        ISQL returncode: 1
        Statement failed, SQLSTATE = 42000
        attempted update of read-only column "C1"."Y"

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column "C2"."Y"

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column "PUBLIC"."TEST"."X"

        Statement failed, SQLSTATE = 42000
        attempted update of read-only column "PUBLIC"."TEST"."Y"
        
        TRG_COUNT 0
    """

    act.expected_stdout = fb3x_checked_stdout if act.is_version('<4') else fb5x_checked_stdout if act.is_version('<6') else fb6x_checked_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
