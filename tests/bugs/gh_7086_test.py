#coding:utf-8

"""
ID:          issue-7086
ISSUE:       7086
TITLE:       PSQL and SQL profiler
NOTES:
    [21.02.2023] pzotov
    Test verifies only example from doc/sql.extensions/README.profiler.md
    More complex checks will be implementer later.
    Checked on 5.0.0.958 SS/CS.
"""

import pytest
from firebird.qa import *

# Output contains lot of data with concrete values for attachment_id, timestamps etc.
# We have to check only presense of such lines and ignore these values:
ptn_list = [
     'ATTACHMENT_ID'
    ,'START_TIMESTAMP'
    ,'FINISH_TIMESTAMP'
    ,'SQL_TEXT'
    ,'LINE_NUM'
    ,'COLUMN_NUM'
    ,'MIN_ELAPSED_TIME'
    ,'MAX_ELAPSED_TIME'
    ,'TOTAL_ELAPSED_TIME'
    ,'AVG_ELAPSED_TIME'
    ,'STATEMENT_ID'
    ,'OPEN_MIN_ELAPSED_TIME'
    ,'OPEN_MAX_ELAPSED_TIME'
    ,'OPEN_TOTAL_ELAPSED_TIME'
    ,'OPEN_AVG_ELAPSED_TIME'
    ,'FETCH_COUNTER'
    ,'FETCH_MIN_ELAPSED_TIME'
    ,'FETCH_MAX_ELAPSED_TIME'
    ,'FETCH_TOTAL_ELAPSED_TIME'
    ,'FETCH_AVG_ELAPSED_TIME'
    ,'OPEN_FETCH_TOTAL_ELAPSED_TIME'
    ,'REQUEST_ID'
    ,'STATEMENT_ID'
    ,'CALLER_REQUEST_ID'
    ,'START_TIMESTAMP'
    ,'FINISH_TIMESTAMP'
    ,'TOTAL_ELAPSED_TIME'
]
sub_list = [ (x+' .*', x) for x in ptn_list ]

substitutions = [ ('[ \t]+', ' ') ] +  sub_list

db = db_factory()

test_script = """
    set list on;
    create table tab (
        id integer not null,
        val integer not null
    );

    set term ^;

    create or alter function mult(p1 integer, p2 integer) returns integer
    as
    begin
        return p1 * p2;
    end^

    create or alter procedure ins
    as
        declare n integer = 1;
    begin
        while (n <= 1000)
        do
        begin
            if (mod(n, 2) = 1) then
                insert into tab values (:n, mult(:n, 2));
            n = n + 1;
        end
    end^

    set term ;^

    -- Start profiling

    select rdb$profiler.start_session('profile session 1') from rdb$database;

    set term ^;

    execute block
    as
    begin
        execute procedure ins;
        delete from tab;
    end^

    set term ;^

    execute procedure rdb$profiler.finish_session(true);

    execute procedure ins;

    select rdb$profiler.start_session('profile session 2') from rdb$database;

    select mod(id, 5),
           sum(val)
      from tab
      where id <= 50
      group by mod(id, 5)
      order by sum(val);

    execute procedure rdb$profiler.finish_session(true);

    -- Data analysis

    commit;
    set transaction read committed;

    set count on;

    ---  [ 1 ] ---
    select * from plg$prof_sessions
    order by profile_id
    ;
    ---  [ 2 ] ---
    select -- * 
        profile_id
        ,statement_type
        ,sql_text
        ,line_num
        ,column_num
        ,counter
        ,min_elapsed_time
        ,max_elapsed_time
        ,total_elapsed_time
        ,avg_elapsed_time
    from plg$prof_psql_stats_view p
    order by p.profile_id,
             p.statement_id,
             p.line_num,
             p.column_num
    ;
    ---  [ 3 ] ---
    select
        profile_id
       ,statement_id
       ,statement_type
       ,package_name
       ,routine_name
       ,parent_statement_id
       ,parent_statement_type
       ,parent_routine_name
       ,sql_text
       ,cursor_id
       ,cursor_name
       ,cursor_line_num
       ,cursor_column_num
       ,record_source_id
       ,parent_record_source_id
       ,access_path
       ,open_counter
       ,open_min_elapsed_time
       ,open_max_elapsed_time
       ,open_total_elapsed_time
       ,open_avg_elapsed_time
       ,fetch_counter
       ,fetch_min_elapsed_time
       ,fetch_max_elapsed_time
       ,fetch_total_elapsed_time
       ,fetch_avg_elapsed_time
       ,open_fetch_total_elapsed_time
    from plg$prof_record_source_stats_view p
    order by p.profile_id,
             p.statement_id
    ;
    ---  [ 4 ] ---
    select -- preq.*
        preq.profile_id
        ,preq.request_id
        ,preq.statement_id
        ,preq.caller_request_id
        ,preq.start_timestamp
        ,preq.finish_timestamp
        ,preq.total_elapsed_time
      from plg$prof_requests preq
      join plg$prof_sessions pses
        on pses.profile_id = preq.profile_id and
           pses.description = 'profile session 1'
      order by preq.profile_id,
               preq.statement_id,
               preq.request_id
    ;
    ---  [ 5 ] ---
    select -- pstat.*
        pstat.profile_id
        ,pstat.request_id
        ,pstat.line_num
        ,pstat.column_num
        ,pstat.statement_id
        ,pstat.counter
        ,pstat.min_elapsed_time
        ,pstat.max_elapsed_time
        ,pstat.total_elapsed_time
      from plg$prof_psql_stats pstat
      join plg$prof_sessions pses
        on pses.profile_id = pstat.profile_id and
           pses.description = 'profile session 1'
      order by pstat.profile_id,
               pstat.statement_id,
               pstat.request_id,
               pstat.line_num,
               pstat.column_num
    ;
    ---  [ 6 ] ---
    select -- pstat.*
         pstat.profile_id
        ,pstat.request_id
        ,pstat.cursor_id
        ,pstat.record_source_id
        ,pstat.statement_id
        ,pstat.open_counter
        ,pstat.open_min_elapsed_time
        ,pstat.open_max_elapsed_time
        ,pstat.open_total_elapsed_time
        ,pstat.fetch_counter
        ,pstat.fetch_min_elapsed_time
        ,pstat.fetch_max_elapsed_time
        ,pstat.fetch_total_elapsed_time
      from plg$prof_record_source_stats pstat
      join plg$prof_sessions pses
        on pses.profile_id = pstat.profile_id and
           pses.description = 'profile session 2'
      order by pstat.profile_id,
               pstat.statement_id,
               pstat.request_id,
               pstat.cursor_id,
               pstat.record_source_id
    ;
"""

act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    START_SESSION                   1
    START_SESSION                   2

    MOD                             1
    SUM                             210

    MOD                             3
    SUM                             230

    MOD                             0
    SUM                             250

    MOD                             2
    SUM                             270

    MOD                             4
    SUM                             290


    PROFILE_ID                      1
    ATTACHMENT_ID                   3
    USER_NAME                       SYSDBA                                                                                                                                                                                                                                                      
    DESCRIPTION                     profile session 1
    START_TIMESTAMP                 2023-02-21 19:02:04.5080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2130 Europe/Moscow

    PROFILE_ID                      2
    ATTACHMENT_ID                   3
    USER_NAME                       SYSDBA                                                                                                                                                                                                                                                      
    DESCRIPTION                     profile session 2
    START_TIMESTAMP                 2023-02-21 19:02:05.3250 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.3310 Europe/Moscow


    Records affected: 2

    PROFILE_ID                      1
    STATEMENT_TYPE                  BLOCK
    SQL_TEXT                        82:1
    execute block
        as
        begin
            execute procedure ins;
            delete from tab;
        end
    LINE_NUM                        4
    COLUMN_NUM                      9
    COUNTER                         1
    MIN_ELAPSED_TIME                40985
    MAX_ELAPSED_TIME                40985
    TOTAL_ELAPSED_TIME              40985
    AVG_ELAPSED_TIME                40985

    PROFILE_ID                      1
    STATEMENT_TYPE                  BLOCK
    SQL_TEXT                        82:1
    execute block
        as
        begin
            execute procedure ins;
            delete from tab;
        end
    LINE_NUM                        5
    COLUMN_NUM                      9
    COUNTER                         1
    MIN_ELAPSED_TIME                4955
    MAX_ELAPSED_TIME                4955
    TOTAL_ELAPSED_TIME              4955
    AVG_ELAPSED_TIME                4955

    PROFILE_ID                      1
    STATEMENT_TYPE                  PROCEDURE
    SQL_TEXT                        <null>
    LINE_NUM                        3
    COLUMN_NUM                      9
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5
    AVG_ELAPSED_TIME                5

    PROFILE_ID                      1
    STATEMENT_TYPE                  PROCEDURE
    SQL_TEXT                        <null>
    LINE_NUM                        5
    COLUMN_NUM                      9
    COUNTER                         1001
    MIN_ELAPSED_TIME                0
    MAX_ELAPSED_TIME                16
    TOTAL_ELAPSED_TIME              1218
    AVG_ELAPSED_TIME                1

    PROFILE_ID                      1
    STATEMENT_TYPE                  PROCEDURE
    SQL_TEXT                        <null>
    LINE_NUM                        8
    COLUMN_NUM                      13
    COUNTER                         1000
    MIN_ELAPSED_TIME                0
    MAX_ELAPSED_TIME                7
    TOTAL_ELAPSED_TIME              1211
    AVG_ELAPSED_TIME                1

    PROFILE_ID                      1
    STATEMENT_TYPE                  PROCEDURE
    SQL_TEXT                        <null>
    LINE_NUM                        9
    COLUMN_NUM                      17
    COUNTER                         500
    MIN_ELAPSED_TIME                66
    MAX_ELAPSED_TIME                189
    TOTAL_ELAPSED_TIME              35885
    AVG_ELAPSED_TIME                71

    PROFILE_ID                      1
    STATEMENT_TYPE                  PROCEDURE
    SQL_TEXT                        <null>
    LINE_NUM                        10
    COLUMN_NUM                      13
    COUNTER                         1000
    MIN_ELAPSED_TIME                1
    MAX_ELAPSED_TIME                8
    TOTAL_ELAPSED_TIME              2565
    AVG_ELAPSED_TIME                2

    PROFILE_ID                      1
    STATEMENT_TYPE                  FUNCTION
    SQL_TEXT                        <null>
    LINE_NUM                        4
    COLUMN_NUM                      9
    COUNTER                         500
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                30
    TOTAL_ELAPSED_TIME              1879
    AVG_ELAPSED_TIME                3


    Records affected: 8

    PROFILE_ID                      1
    STATEMENT_ID                    276
    STATEMENT_TYPE                  BLOCK
    PACKAGE_NAME                    <null>
    ROUTINE_NAME                    <null>
    PARENT_STATEMENT_ID             <null>
    PARENT_STATEMENT_TYPE           <null>
    PARENT_ROUTINE_NAME             <null>
    SQL_TEXT                        82:0
    select rdb$profiler.start_session('profile session 1') from rdb$database
    CURSOR_ID                       1
    CURSOR_NAME                     <null>
    CURSOR_LINE_NUM                 <null>
    CURSOR_COLUMN_NUM               <null>
    RECORD_SOURCE_ID                1
    PARENT_RECORD_SOURCE_ID         <null>
    ACCESS_PATH                     
    -> Table "RDB$DATABASE" Full Scan
    OPEN_COUNTER                    0
    OPEN_MIN_ELAPSED_TIME           0
    OPEN_MAX_ELAPSED_TIME           0
    OPEN_TOTAL_ELAPSED_TIME         0
    OPEN_AVG_ELAPSED_TIME           <null>
    FETCH_COUNTER                   1
    FETCH_MIN_ELAPSED_TIME          32
    FETCH_MAX_ELAPSED_TIME          32
    FETCH_TOTAL_ELAPSED_TIME        32
    FETCH_AVG_ELAPSED_TIME          32
    OPEN_FETCH_TOTAL_ELAPSED_TIME   32

    PROFILE_ID                      1
    STATEMENT_ID                    5417
    STATEMENT_TYPE                  BLOCK
    PACKAGE_NAME                    <null>
    ROUTINE_NAME                    <null>
    PARENT_STATEMENT_ID             <null>
    PARENT_STATEMENT_TYPE           <null>
    PARENT_ROUTINE_NAME             <null>
    SQL_TEXT                        82:1
    execute block
        as
        begin
            execute procedure ins;
            delete from tab;
        end
    CURSOR_ID                       1
    CURSOR_NAME                     <null>
    CURSOR_LINE_NUM                 5
    CURSOR_COLUMN_NUM               9
    RECORD_SOURCE_ID                1
    PARENT_RECORD_SOURCE_ID         <null>
    ACCESS_PATH                     
    -> Table "TAB" Full Scan
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           17
    OPEN_MAX_ELAPSED_TIME           17
    OPEN_TOTAL_ELAPSED_TIME         17
    OPEN_AVG_ELAPSED_TIME           17
    FETCH_COUNTER                   501
    FETCH_MIN_ELAPSED_TIME          1
    FETCH_MAX_ELAPSED_TIME          11
    FETCH_TOTAL_ELAPSED_TIME        843
    FETCH_AVG_ELAPSED_TIME          1
    OPEN_FETCH_TOTAL_ELAPSED_TIME   860

    PROFILE_ID                      2
    STATEMENT_ID                    7029
    STATEMENT_TYPE                  BLOCK
    PACKAGE_NAME                    <null>
    ROUTINE_NAME                    <null>
    PARENT_STATEMENT_ID             <null>
    PARENT_STATEMENT_TYPE           <null>
    PARENT_ROUTINE_NAME             <null>
    SQL_TEXT                        82:2
    select rdb$profiler.start_session('profile session 2') from rdb$database
    CURSOR_ID                       1
    CURSOR_NAME                     <null>
    CURSOR_LINE_NUM                 <null>
    CURSOR_COLUMN_NUM               <null>
    RECORD_SOURCE_ID                1
    PARENT_RECORD_SOURCE_ID         <null>
    ACCESS_PATH                     
    -> Table "RDB$DATABASE" Full Scan
    OPEN_COUNTER                    0
    OPEN_MIN_ELAPSED_TIME           0
    OPEN_MAX_ELAPSED_TIME           0
    OPEN_TOTAL_ELAPSED_TIME         0
    OPEN_AVG_ELAPSED_TIME           <null>
    FETCH_COUNTER                   1
    FETCH_MIN_ELAPSED_TIME          31
    FETCH_MAX_ELAPSED_TIME          31
    FETCH_TOTAL_ELAPSED_TIME        31
    FETCH_AVG_ELAPSED_TIME          31
    OPEN_FETCH_TOTAL_ELAPSED_TIME   31

    PROFILE_ID                      2
    STATEMENT_ID                    7037
    STATEMENT_TYPE                  BLOCK
    PACKAGE_NAME                    <null>
    ROUTINE_NAME                    <null>
    PARENT_STATEMENT_ID             <null>
    PARENT_STATEMENT_TYPE           <null>
    PARENT_ROUTINE_NAME             <null>
    SQL_TEXT                        82:3
    select mod(id, 5),
               sum(val)
          from tab
          where id <= 50
          group by mod(id, 5)
          order by sum(val)
    CURSOR_ID                       1
    CURSOR_NAME                     <null>
    CURSOR_LINE_NUM                 <null>
    CURSOR_COLUMN_NUM               <null>
    RECORD_SOURCE_ID                2
    PARENT_RECORD_SOURCE_ID         1
    ACCESS_PATH                     
    -> Aggregate
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           1463
    OPEN_MAX_ELAPSED_TIME           1463
    OPEN_TOTAL_ELAPSED_TIME         1463
    OPEN_AVG_ELAPSED_TIME           1463
    FETCH_COUNTER                   6
    FETCH_MIN_ELAPSED_TIME          1
    FETCH_MAX_ELAPSED_TIME          34
    FETCH_TOTAL_ELAPSED_TIME        90
    FETCH_AVG_ELAPSED_TIME          15
    OPEN_FETCH_TOTAL_ELAPSED_TIME   1553

    PROFILE_ID                      2
    STATEMENT_ID                    7037
    STATEMENT_TYPE                  BLOCK
    PACKAGE_NAME                    <null>
    ROUTINE_NAME                    <null>
    PARENT_STATEMENT_ID             <null>
    PARENT_STATEMENT_TYPE           <null>
    PARENT_ROUTINE_NAME             <null>
    SQL_TEXT                        82:3
    select mod(id, 5),
               sum(val)
          from tab
          where id <= 50
          group by mod(id, 5)
          order by sum(val)
    CURSOR_ID                       1
    CURSOR_NAME                     <null>
    CURSOR_LINE_NUM                 <null>
    CURSOR_COLUMN_NUM               <null>
    RECORD_SOURCE_ID                3
    PARENT_RECORD_SOURCE_ID         2
    ACCESS_PATH                     
    -> Sort (record length: 44, key length: 8)
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           1459
    OPEN_MAX_ELAPSED_TIME           1459
    OPEN_TOTAL_ELAPSED_TIME         1459
    OPEN_AVG_ELAPSED_TIME           1459
    FETCH_COUNTER                   26
    FETCH_MIN_ELAPSED_TIME          0
    FETCH_MAX_ELAPSED_TIME          4
    FETCH_TOTAL_ELAPSED_TIME        25
    FETCH_AVG_ELAPSED_TIME          0
    OPEN_FETCH_TOTAL_ELAPSED_TIME   1484

    PROFILE_ID                      2
    STATEMENT_ID                    7037
    STATEMENT_TYPE                  BLOCK
    PACKAGE_NAME                    <null>
    ROUTINE_NAME                    <null>
    PARENT_STATEMENT_ID             <null>
    PARENT_STATEMENT_TYPE           <null>
    PARENT_ROUTINE_NAME             <null>
    SQL_TEXT                        82:3
    select mod(id, 5),
               sum(val)
          from tab
          where id <= 50
          group by mod(id, 5)
          order by sum(val)
    CURSOR_ID                       1
    CURSOR_NAME                     <null>
    CURSOR_LINE_NUM                 <null>
    CURSOR_COLUMN_NUM               <null>
    RECORD_SOURCE_ID                4
    PARENT_RECORD_SOURCE_ID         3
    ACCESS_PATH                     
    -> Filter
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           8
    OPEN_MAX_ELAPSED_TIME           8
    OPEN_TOTAL_ELAPSED_TIME         8
    OPEN_AVG_ELAPSED_TIME           8
    FETCH_COUNTER                   26
    FETCH_MIN_ELAPSED_TIME          2
    FETCH_MAX_ELAPSED_TIME          959
    FETCH_TOTAL_ELAPSED_TIME        1395
    FETCH_AVG_ELAPSED_TIME          53
    OPEN_FETCH_TOTAL_ELAPSED_TIME   1403

    PROFILE_ID                      2
    STATEMENT_ID                    7037
    STATEMENT_TYPE                  BLOCK
    PACKAGE_NAME                    <null>
    ROUTINE_NAME                    <null>
    PARENT_STATEMENT_ID             <null>
    PARENT_STATEMENT_TYPE           <null>
    PARENT_ROUTINE_NAME             <null>
    SQL_TEXT                        82:3
    select mod(id, 5),
               sum(val)
          from tab
          where id <= 50
          group by mod(id, 5)
          order by sum(val)
    CURSOR_ID                       1
    CURSOR_NAME                     <null>
    CURSOR_LINE_NUM                 <null>
    CURSOR_COLUMN_NUM               <null>
    RECORD_SOURCE_ID                5
    PARENT_RECORD_SOURCE_ID         4
    ACCESS_PATH                     
    -> Table "TAB" Full Scan
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           2
    OPEN_MAX_ELAPSED_TIME           2
    OPEN_TOTAL_ELAPSED_TIME         2
    OPEN_AVG_ELAPSED_TIME           2
    FETCH_COUNTER                   501
    FETCH_MIN_ELAPSED_TIME          1
    FETCH_MAX_ELAPSED_TIME          375
    FETCH_TOTAL_ELAPSED_TIME        1033
    FETCH_AVG_ELAPSED_TIME          2
    OPEN_FETCH_TOTAL_ELAPSED_TIME   1035

    PROFILE_ID                      2
    STATEMENT_ID                    7037
    STATEMENT_TYPE                  BLOCK
    PACKAGE_NAME                    <null>
    ROUTINE_NAME                    <null>
    PARENT_STATEMENT_ID             <null>
    PARENT_STATEMENT_TYPE           <null>
    PARENT_ROUTINE_NAME             <null>
    SQL_TEXT                        82:3
    select mod(id, 5),
               sum(val)
          from tab
          where id <= 50
          group by mod(id, 5)
          order by sum(val)
    CURSOR_ID                       1
    CURSOR_NAME                     <null>
    CURSOR_LINE_NUM                 <null>
    CURSOR_COLUMN_NUM               <null>
    RECORD_SOURCE_ID                1
    PARENT_RECORD_SOURCE_ID         <null>
    ACCESS_PATH                     
    -> Sort (record length: 44, key length: 12)
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           1629
    OPEN_MAX_ELAPSED_TIME           1629
    OPEN_TOTAL_ELAPSED_TIME         1629
    OPEN_AVG_ELAPSED_TIME           1629
    FETCH_COUNTER                   6
    FETCH_MIN_ELAPSED_TIME          1
    FETCH_MAX_ELAPSED_TIME          3
    FETCH_TOTAL_ELAPSED_TIME        9
    FETCH_AVG_ELAPSED_TIME          1
    OPEN_FETCH_TOTAL_ELAPSED_TIME   1638


    Records affected: 8

    PROFILE_ID                      1
    REQUEST_ID                      276
    STATEMENT_ID                    276
    CALLER_REQUEST_ID               <null>
    START_TIMESTAMP                 2023-02-21 19:02:05.1940 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1940 Europe/Moscow
    TOTAL_ELAPSED_TIME              2052765

    PROFILE_ID                      1
    REQUEST_ID                      277
    STATEMENT_ID                    277
    CALLER_REQUEST_ID               276
    START_TIMESTAMP                 2023-02-21 19:02:05.1940 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1940 Europe/Moscow
    TOTAL_ELAPSED_TIME              2052492

    PROFILE_ID                      1
    REQUEST_ID                      5417
    STATEMENT_ID                    5417
    CALLER_REQUEST_ID               <null>
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2120 Europe/Moscow
    TOTAL_ELAPSED_TIME              45944

    PROFILE_ID                      1
    REQUEST_ID                      5418
    STATEMENT_ID                    5418
    CALLER_REQUEST_ID               5417
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              40889

    PROFILE_ID                      1
    REQUEST_ID                      5419
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              18

    PROFILE_ID                      1
    REQUEST_ID                      5420
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5421
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5422
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5423
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5424
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5425
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5426
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5427
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5428
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5429
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5430
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5431
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5432
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5433
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5434
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5435
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5436
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5437
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5438
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5439
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5440
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5441
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5442
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5443
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5444
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5445
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5446
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5447
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5448
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5449
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5450
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5451
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1970 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1970 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5452
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5453
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5454
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5455
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5456
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5457
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5458
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5459
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5460
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5461
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5462
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5463
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5464
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5465
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5466
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5467
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5468
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5469
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5470
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5471
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5472
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5473
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5474
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5475
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5476
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5477
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5478
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5479
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5480
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5481
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5482
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5483
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5484
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5485
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5486
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5487
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5488
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1980 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1980 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5489
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5490
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5491
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5492
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5493
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5494
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5495
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5496
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5497
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5498
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5499
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5500
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5501
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5502
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5503
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5504
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5505
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5506
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5507
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5508
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5509
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5510
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5511
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5512
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5513
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5514
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5515
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5516
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5517
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5518
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5519
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5520
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5521
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5522
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5523
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5524
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5525
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.1990 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.1990 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5526
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              16

    PROFILE_ID                      1
    REQUEST_ID                      5527
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5528
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5529
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5530
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5531
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5532
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5533
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5534
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5535
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5536
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5537
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5538
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5539
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5540
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5541
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5542
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5543
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5544
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5545
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5546
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5547
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5548
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5549
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5550
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5551
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5552
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5553
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5554
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5555
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5556
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5557
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5558
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5559
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5560
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5561
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2000 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2000 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5562
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              14

    PROFILE_ID                      1
    REQUEST_ID                      5563
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              13

    PROFILE_ID                      1
    REQUEST_ID                      5564
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5565
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5566
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5567
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5568
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5569
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5570
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5571
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5572
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5573
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5574
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5575
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5576
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5577
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5578
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5579
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5580
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5581
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5582
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5583
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5584
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5585
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5586
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5587
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5588
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5589
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5590
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5591
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5592
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5593
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5594
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5595
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5596
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5597
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2010 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2010 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5598
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              37

    PROFILE_ID                      1
    REQUEST_ID                      5599
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              13

    PROFILE_ID                      1
    REQUEST_ID                      5600
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5601
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5602
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5603
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5604
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5605
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5606
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5607
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5608
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5609
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5610
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5611
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5612
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5613
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5614
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5615
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5616
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5617
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5618
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5619
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5620
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5621
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5622
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5623
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5624
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5625
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5626
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5627
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5628
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5629
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5630
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5631
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5632
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5633
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2020 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5634
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2020 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5635
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5636
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5637
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5638
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5639
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5640
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5641
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5642
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5643
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5644
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5645
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5646
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5647
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5648
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5649
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5650
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5651
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5652
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5653
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5654
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5655
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5656
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5657
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5658
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5659
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5660
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5661
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5662
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5663
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5664
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5665
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5666
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5667
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5668
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5669
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5670
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5671
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2030 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2030 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5672
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              15

    PROFILE_ID                      1
    REQUEST_ID                      5673
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              14

    PROFILE_ID                      1
    REQUEST_ID                      5674
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5675
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5676
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5677
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5678
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5679
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5680
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5681
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5682
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5683
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5684
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5685
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5686
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5687
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5688
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5689
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5690
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5691
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5692
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5693
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5694
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5695
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5696
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5697
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5698
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5699
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5700
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5701
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5702
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5703
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5704
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5705
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5706
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2040 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2040 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5707
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5708
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5709
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5710
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5711
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5712
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5713
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5714
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5715
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5716
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5717
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5718
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5719
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5720
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5721
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5722
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5723
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5724
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5725
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5726
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5727
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5728
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5729
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5730
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5731
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5732
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5733
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5734
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5735
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5736
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5737
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5738
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5739
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5740
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5741
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5742
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5743
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2050 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2050 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5744
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5745
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5746
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5747
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5748
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5749
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5750
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5751
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5752
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5753
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5754
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5755
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5756
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5757
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5758
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5759
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5760
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5761
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5762
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5763
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5764
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5765
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5766
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5767
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5768
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5769
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5770
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5771
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5772
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5773
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5774
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5775
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5776
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5777
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5778
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5779
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2060 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5780
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2060 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5781
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5782
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5783
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5784
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5785
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5786
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5787
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5788
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5789
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5790
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5791
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5792
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5793
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5794
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5795
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5796
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5797
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5798
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5799
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5800
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5801
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5802
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5803
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5804
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5805
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5806
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5807
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5808
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5809
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5810
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5811
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5812
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5813
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5814
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5815
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5816
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2070 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5817
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2070 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5818
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5819
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5820
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5821
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5822
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5823
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5824
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5825
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5826
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5827
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5828
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              11

    PROFILE_ID                      1
    REQUEST_ID                      5829
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5830
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5831
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5832
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5833
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5834
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5835
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5836
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5837
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5838
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5839
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5840
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5841
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5842
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5843
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5844
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5845
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5846
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5847
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5848
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5849
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5850
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5851
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5852
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5853
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2080 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2080 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5854
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5855
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5856
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5857
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5858
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5859
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5860
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5861
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5862
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5863
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5864
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5865
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5866
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5867
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5868
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5869
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5870
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5871
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5872
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5873
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5874
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5875
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5876
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5877
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5878
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5879
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5880
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5881
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5882
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5883
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5884
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5885
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5886
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5887
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5888
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5889
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5890
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5891
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2090 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2090 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5892
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5893
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5894
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5895
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5896
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5897
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5898
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5899
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5900
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5901
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5902
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5903
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5904
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5905
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5906
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5907
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5908
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5909
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5910
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5911
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              9

    PROFILE_ID                      1
    REQUEST_ID                      5912
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5913
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5914
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5915
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5916
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5917
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              10

    PROFILE_ID                      1
    REQUEST_ID                      5918
    STATEMENT_ID                    5419
    CALLER_REQUEST_ID               5418
    START_TIMESTAMP                 2023-02-21 19:02:05.2100 Europe/Moscow
    FINISH_TIMESTAMP                2023-02-21 19:02:05.2100 Europe/Moscow
    TOTAL_ELAPSED_TIME              7


    Records affected: 504

    PROFILE_ID                      1
    REQUEST_ID                      5417
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5417
    COUNTER                         1
    MIN_ELAPSED_TIME                40985
    MAX_ELAPSED_TIME                40985
    TOTAL_ELAPSED_TIME              40985

    PROFILE_ID                      1
    REQUEST_ID                      5417
    LINE_NUM                        5
    COLUMN_NUM                      9
    STATEMENT_ID                    5417
    COUNTER                         1
    MIN_ELAPSED_TIME                4955
    MAX_ELAPSED_TIME                4955
    TOTAL_ELAPSED_TIME              4955

    PROFILE_ID                      1
    REQUEST_ID                      5418
    LINE_NUM                        3
    COLUMN_NUM                      9
    STATEMENT_ID                    5418
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5418
    LINE_NUM                        5
    COLUMN_NUM                      9
    STATEMENT_ID                    5418
    COUNTER                         1001
    MIN_ELAPSED_TIME                0
    MAX_ELAPSED_TIME                16
    TOTAL_ELAPSED_TIME              1218

    PROFILE_ID                      1
    REQUEST_ID                      5418
    LINE_NUM                        8
    COLUMN_NUM                      13
    STATEMENT_ID                    5418
    COUNTER                         1000
    MIN_ELAPSED_TIME                0
    MAX_ELAPSED_TIME                7
    TOTAL_ELAPSED_TIME              1211

    PROFILE_ID                      1
    REQUEST_ID                      5418
    LINE_NUM                        9
    COLUMN_NUM                      17
    STATEMENT_ID                    5418
    COUNTER                         500
    MIN_ELAPSED_TIME                66
    MAX_ELAPSED_TIME                189
    TOTAL_ELAPSED_TIME              35885

    PROFILE_ID                      1
    REQUEST_ID                      5418
    LINE_NUM                        10
    COLUMN_NUM                      13
    STATEMENT_ID                    5418
    COUNTER                         1000
    MIN_ELAPSED_TIME                1
    MAX_ELAPSED_TIME                8
    TOTAL_ELAPSED_TIME              2565

    PROFILE_ID                      1
    REQUEST_ID                      5419
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                8
    MAX_ELAPSED_TIME                8
    TOTAL_ELAPSED_TIME              8

    PROFILE_ID                      1
    REQUEST_ID                      5420
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5421
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5422
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5423
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5424
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5425
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5426
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5427
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5428
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5429
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5430
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5431
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5432
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5433
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5434
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5435
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5436
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5437
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5438
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5439
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5440
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5441
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5442
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5443
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5444
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5445
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5446
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5447
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5448
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5449
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5450
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5451
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5452
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5453
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5454
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5455
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5456
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5457
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5458
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5459
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5460
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5461
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5462
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5463
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5464
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5465
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5466
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5467
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5468
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5469
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5470
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5471
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5472
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5473
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5474
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5475
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5476
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5477
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5478
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5479
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5480
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5481
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5482
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5483
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5484
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5485
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5486
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5487
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5488
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5489
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5490
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5491
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5492
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5493
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5494
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5495
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5496
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5497
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5498
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5499
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5500
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5501
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5502
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5503
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5504
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5505
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5506
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5507
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5508
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5509
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5510
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5511
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5512
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5513
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5514
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5515
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5516
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5517
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5518
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5519
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5520
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5521
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5522
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5523
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5524
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5525
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5526
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                7
    MAX_ELAPSED_TIME                7
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5527
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5528
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5529
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5530
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5531
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5532
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5533
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5534
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5535
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5536
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5537
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5538
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5539
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5540
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5541
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5542
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5543
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5544
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5545
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5546
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5547
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5548
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5549
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5550
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5551
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5552
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5553
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5554
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5555
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5556
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5557
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5558
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5559
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5560
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5561
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5562
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                7
    MAX_ELAPSED_TIME                7
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5563
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                6
    MAX_ELAPSED_TIME                6
    TOTAL_ELAPSED_TIME              6

    PROFILE_ID                      1
    REQUEST_ID                      5564
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5565
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5566
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5567
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5568
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5569
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5570
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5571
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5572
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5573
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5574
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5575
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5576
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5577
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5578
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5579
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5580
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5581
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5582
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5583
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5584
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5585
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5586
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5587
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5588
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5589
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5590
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5591
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5592
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5593
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5594
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5595
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5596
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5597
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5598
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                30
    MAX_ELAPSED_TIME                30
    TOTAL_ELAPSED_TIME              30

    PROFILE_ID                      1
    REQUEST_ID                      5599
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                6
    MAX_ELAPSED_TIME                6
    TOTAL_ELAPSED_TIME              6

    PROFILE_ID                      1
    REQUEST_ID                      5600
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5601
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5602
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5603
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5604
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5605
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5606
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5607
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5608
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5609
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5610
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5611
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5612
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5613
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5614
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5615
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5616
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5617
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5618
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5619
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5620
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5621
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5622
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5623
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5624
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5625
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5626
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5627
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5628
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5629
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5630
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5631
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5632
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5633
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5634
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5635
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5636
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5637
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5638
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5639
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5640
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5641
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5642
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5643
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5644
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5645
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5646
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5647
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5648
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5649
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5650
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5651
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5652
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5653
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5654
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5655
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5656
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5657
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5658
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5659
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5660
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5661
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5662
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5663
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5664
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5665
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5666
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5667
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5668
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5669
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5670
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5671
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5672
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                7
    MAX_ELAPSED_TIME                7
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5673
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                7
    MAX_ELAPSED_TIME                7
    TOTAL_ELAPSED_TIME              7

    PROFILE_ID                      1
    REQUEST_ID                      5674
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5675
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5676
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5677
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5678
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5679
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5680
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5681
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5682
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5683
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5684
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5685
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5686
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5687
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5688
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5689
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5690
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5691
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5692
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5693
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5694
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5695
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5696
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5697
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5698
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5699
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5700
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5701
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5702
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5703
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5704
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5705
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5706
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5707
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5708
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5709
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5710
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5711
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5712
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5713
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5714
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5715
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5716
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5717
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5718
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5719
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5720
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5721
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5722
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5723
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5724
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5725
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5726
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5727
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5728
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5729
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5730
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5731
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5732
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5733
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5734
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5735
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5736
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5737
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5738
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5739
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5740
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5741
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5742
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5743
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5744
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5745
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5746
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5747
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5748
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5749
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5750
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5751
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5752
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5753
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5754
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5755
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5756
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5757
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5758
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5759
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5760
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5761
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5762
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5763
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5764
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5765
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5766
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5767
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5768
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5769
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5770
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5771
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5772
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5773
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5774
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5775
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5776
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5777
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5778
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5779
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5780
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5781
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5782
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5783
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5784
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5785
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5786
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5787
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5788
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5789
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5790
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5791
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5792
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5793
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5794
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5795
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5796
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5797
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5798
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5799
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5800
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5801
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5802
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5803
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5804
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5805
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5806
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5807
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5808
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5809
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5810
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5811
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5812
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5813
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5814
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5815
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5816
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5817
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5818
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5819
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5820
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5821
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5822
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5823
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5824
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5825
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5826
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5827
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5828
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5829
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5830
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5831
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5832
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5833
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5834
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5835
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5836
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5837
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5838
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5839
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5840
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5841
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5842
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5843
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5844
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5845
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5846
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5847
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5848
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5849
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5850
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5851
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5852
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5853
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5854
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5855
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5856
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5857
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5858
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5859
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5860
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5861
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5862
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5863
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5864
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                5
    MAX_ELAPSED_TIME                5
    TOTAL_ELAPSED_TIME              5

    PROFILE_ID                      1
    REQUEST_ID                      5865
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5866
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5867
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5868
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5869
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5870
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5871
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5872
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5873
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5874
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5875
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5876
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5877
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5878
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5879
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5880
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5881
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5882
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5883
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5884
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5885
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5886
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5887
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5888
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5889
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5890
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5891
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5892
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5893
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5894
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5895
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5896
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5897
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5898
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5899
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5900
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5901
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5902
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5903
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5904
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5905
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5906
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5907
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5908
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5909
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5910
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5911
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5912
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5913
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5914
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5915
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                3
    MAX_ELAPSED_TIME                3
    TOTAL_ELAPSED_TIME              3

    PROFILE_ID                      1
    REQUEST_ID                      5916
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5917
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4

    PROFILE_ID                      1
    REQUEST_ID                      5918
    LINE_NUM                        4
    COLUMN_NUM                      9
    STATEMENT_ID                    5419
    COUNTER                         1
    MIN_ELAPSED_TIME                4
    MAX_ELAPSED_TIME                4
    TOTAL_ELAPSED_TIME              4


    Records affected: 507

    PROFILE_ID                      2
    REQUEST_ID                      7029
    CURSOR_ID                       1
    RECORD_SOURCE_ID                1
    STATEMENT_ID                    7029
    OPEN_COUNTER                    0
    OPEN_MIN_ELAPSED_TIME           0
    OPEN_MAX_ELAPSED_TIME           0
    OPEN_TOTAL_ELAPSED_TIME         0
    FETCH_COUNTER                   1
    FETCH_MIN_ELAPSED_TIME          31
    FETCH_MAX_ELAPSED_TIME          31
    FETCH_TOTAL_ELAPSED_TIME        31

    PROFILE_ID                      2
    REQUEST_ID                      7037
    CURSOR_ID                       1
    RECORD_SOURCE_ID                1
    STATEMENT_ID                    7037
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           1629
    OPEN_MAX_ELAPSED_TIME           1629
    OPEN_TOTAL_ELAPSED_TIME         1629
    FETCH_COUNTER                   6
    FETCH_MIN_ELAPSED_TIME          1
    FETCH_MAX_ELAPSED_TIME          3
    FETCH_TOTAL_ELAPSED_TIME        9

    PROFILE_ID                      2
    REQUEST_ID                      7037
    CURSOR_ID                       1
    RECORD_SOURCE_ID                2
    STATEMENT_ID                    7037
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           1463
    OPEN_MAX_ELAPSED_TIME           1463
    OPEN_TOTAL_ELAPSED_TIME         1463
    FETCH_COUNTER                   6
    FETCH_MIN_ELAPSED_TIME          1
    FETCH_MAX_ELAPSED_TIME          34
    FETCH_TOTAL_ELAPSED_TIME        90

    PROFILE_ID                      2
    REQUEST_ID                      7037
    CURSOR_ID                       1
    RECORD_SOURCE_ID                3
    STATEMENT_ID                    7037
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           1459
    OPEN_MAX_ELAPSED_TIME           1459
    OPEN_TOTAL_ELAPSED_TIME         1459
    FETCH_COUNTER                   26
    FETCH_MIN_ELAPSED_TIME          0
    FETCH_MAX_ELAPSED_TIME          4
    FETCH_TOTAL_ELAPSED_TIME        25

    PROFILE_ID                      2
    REQUEST_ID                      7037
    CURSOR_ID                       1
    RECORD_SOURCE_ID                4
    STATEMENT_ID                    7037
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           8
    OPEN_MAX_ELAPSED_TIME           8
    OPEN_TOTAL_ELAPSED_TIME         8
    FETCH_COUNTER                   26
    FETCH_MIN_ELAPSED_TIME          2
    FETCH_MAX_ELAPSED_TIME          959
    FETCH_TOTAL_ELAPSED_TIME        1395

    PROFILE_ID                      2
    REQUEST_ID                      7037
    CURSOR_ID                       1
    RECORD_SOURCE_ID                5
    STATEMENT_ID                    7037
    OPEN_COUNTER                    1
    OPEN_MIN_ELAPSED_TIME           2
    OPEN_MAX_ELAPSED_TIME           2
    OPEN_TOTAL_ELAPSED_TIME         2
    FETCH_COUNTER                   501
    FETCH_MIN_ELAPSED_TIME          1
    FETCH_MAX_ELAPSED_TIME          375
    FETCH_TOTAL_ELAPSED_TIME        1033


    Records affected: 6
"""

@pytest.mark.version('>=5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
