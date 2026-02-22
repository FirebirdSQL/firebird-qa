#coding:utf-8

"""
ID:          issue-8418
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/8418
TITLE:       UNLIST function. Check output for different returning types
DESCRIPTION: Provided by red-soft. Original file name: "unlist.test_returning_types.py"
NOTES:
    [28.12.2025] pzotov
        Changed substitutions: value +/-0e0 can be displayed with 16 digits after decimal point.
        "Excessive" 16th digit (zero) is supressed. Detected on Windows-10, Intel Xeon W-2123.
        Discussed with FB-team, key note by Vlad: 29.12.2025 11:53, ucrtbase.dll can differ.
    [22.06.2025] pzotov
        Re-implemented: use python_act in order to see gdscodes list. Adjusted substitutions.
        Organize statements into dict in order to make easy their search in case when test fails.
        Adusted output to actual: no error raises in for statements when returning datatype is
        varchar / nvarchar and NO length is specified, e.g.:
            select * from unlist('text' returning varchar) as a(unlist_varchar_03);
        Changed at #d32276b8 'Support VARCHAR without explicit length'
        Previously such expressions failed with 'SQLSTATE = 42000 / ... / Token unknown -)'
        Checked on 6.0.0.1461.
"""
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

db = db_factory(init = 'create domain test_domain as varchar(8);')

DELIMITER_LINE = '-+=' * 30

SELECTED_TIMEZONE = 'Indian/Cocos'

substitutions= [ ('[\t ]+', ' '), (' 0.0000000000000000', ' 0.000000000000000'), ('(-)?At line \\d+.*', 'At line'), ('(-)?Token unknown.*', 'Token unknown') ]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    qry_map = {
        # bigint
         10000 : "select * from unlist('-9223372036854775808,9223372036854775807' returning bigint) as a(unlist_bigint_01)"
        ,10100 : "select * from unlist('-9223372036854775809' returning bigint) as a(unlist_bigint_02)"

        # Must raise two time: SQLSTATE = 22003 / ... / -numeric value is out of range:
        ,10150 : "select * from unlist('9223372036854775808' returning bigint) as a(unlist_bigint_03)"

        # boolean
        ,10200 : "select * from unlist('true,false' returning boolean) as a(unlist_boolean_01)"

        # SQLSTATE = 22018 / conversion error from string "right":
        ,10250 : "select * from unlist('right' returning boolean) as a(unlist_boolean_02)"

        # binary(n): following must pass:
        ,10300 : "select * from unlist('1111,12345678' returning binary(8)) as a(unlist_binary_01)"
        ,10350 : "select * from unlist('text,texttext' returning binary(8)) as a(unlist_binary_02)"

        # char(n)

        # must pass:
        ,10400 : "select * from unlist('text,texttext,1243' returning char(8)) as a(unlist_char_01)"
        
        # must raise SQLSTATE = 22001 / ... / -string right truncation / -expected length 1, actual 4:
        ,10450 : "select * from unlist('text' returning char) as a(unlist_char_02)"

        # must raise SQLSTATE = 42000 / ... / -Positive value expected:
        ,10460 : "select * from unlist('text' returning char(0)) as a(unlist_char_03)"

        # date
        ,20000 : "select * from unlist('1.01.0001,31.12.9999,8/06/2315,1245-12-01,5555/12/28' returning date) as a(unlist_date_01)"

        # SQLSTATE = 22008 / value exceeds the range for valid dates:
        ,20100 : "select * from unlist('1.01.0000' returning date) as a(unlist_date_02)"

        # SQLSTATE = 22018 / conversion error from string "1.01.10000":
        ,20200 : "select * from unlist('1.01.10000' returning date) as a(unlist_date_03)"

        # must PASS:
        ,20300 : "select extract( day from (select * from unlist('1.01.2201' returning date) as a(unlist_date_04) ) ) from rdb$database"

        # decimal(n, m)
        ,21000 : "select * from unlist('4,2.00,5.83,23.01' returning dec(4,2)) as a(unlist_decimal_01)"
        ,21100 : "select * from unlist('55555555555555555555555555555555555555' returning dec(38,0)) as a(unlist_decimal_02)"

        # SQLSTATE = HY104 / ... / -Precision must be from 1 to 38    
        ,21200 : "select * from unlist('555555555555555555555555555555555555555555555555555555' returning dec(54,0)) as a(unlist_decimal_03)"

        # decfloat (16|34): following must pass:
        ,22000 : "select * from unlist('4,2.00,5.83,23.00000000000001,24.000000000000011' returning decfloat(16)) as a(unlist_decfloat16_01)"

        ,22100 : "select * from unlist('4,2.00,5.83,23.00000000000001000000000000000001,24.000000000000010000000000000000011' returning decfloat(34)) as a(unlist_decfloat34_01)"

        # double precision
        # TODO LATER: investigate why such strange low limit for least positive number, '9.9e-307':
        ,25000 : "select * from unlist('0e0,-0e0,9.9e-307,1.7976931348623157e308,4,2.00,5.83,23.00000000000001, 24.000000000000011' returning double precision) as a(unlist_double_01)"

        # float
        ,27000 : "select * from unlist('4,2.00,5.83,23.000001, 24.0000011' returning float) as a(unlist_float_01)"

        # int
        ,30000 : "select * from unlist('-2147483648,2147483647' returning int) as a(unlist_int_01)"

        # SQLSTATE = 22003 / ... / -numeric value is out of range:
        ,30100 : "select * from unlist('-2147483649' returning int) as a(unlist_int_02)"

        # SQLSTATE = 22003 / ... / -numeric value is out of range:
        ,30200 : "select * from unlist('2147483648' returning int) as a(unlist_int_03)"

        # int128
        ,33000 : "select * from unlist('-170141183460469231731687303715884105728, 170141183460469231731687303715884105727' returning int128) as a(unlist_int128_01)"

        # SQLSTATE = 22003 / ... / -numeric value is out of range:
        ,33100 : "select * from unlist('-170141183460469231731687303715884105729' returning int128) as a(unlist_int128_01)"

        # SQLSTATE = 22003 / ... / -numeric value is out of range:
        ,33200 : "select * from unlist('170141183460469231731687303715884105728' returning int128) as a(unlist_int128_01)"


        # national character (n)
        ,35000 : "select * from unlist('qwer,asdf,zxcv' returning nchar(8)) as a(unlist_nchar_01)"

        # must raise SQLSTATE = 22001 / ... / -string right truncation / -expected length 1, actual 4:
        ,35100 : "select * from unlist('tyui' returning nchar) as a(unlist_nchar_02)"

        # must raise SQLSTATE = 42000 / ... / -Positive value expected:
        ,35200 : "select * from unlist('ghjk' returning nchar(0)) as a(unlist_nchar_03)"

        # varchar
        ,37000 : "select * from unlist('text,texttext,1243' returning varchar(8)) as a(unlist_varchar_01)"

        # SQLSTATE = 22001 / -string right truncation / -expected length 8, actual 12:
        ,37100 : "select * from unlist('texttexttext' returning varchar(8)) as a(unlist_varchar_02)"

        # -Token unknown ... -)
        ,37200 : "select * from unlist('text' returning varchar) as a(unlist_varchar_03)"

        # Positive value expected
        ,37300 : "select * from unlist('text' returning varchar(0)) as a(unlist_varchar_04)"

        # national character varying (n)
        ,38000 : "select * from unlist('text,texttext,1243' returning nchar varying(8)) as a(unlist_nvarchar_01)"

        # SQLSTATE = 22001 / -string right truncation / -expected length 8, actual 12:
        ,38100 : "select * from unlist('texttexttext' returning nchar varying(8)) as a(unlist_nvarchar_02)"

        # -Token unknown ... -)
        ,38200 : "select * from unlist('text' returning nchar varying) as a(unlist_nvarchar_03)"

        # Positive value expected
        ,38300 : "select * from unlist('text' returning nchar varying(0)) as a(unlist_nvarchar_04)"

        # numeric(n, m) = decimal(n, m)

        # smallint
        ,40000 : "select * from unlist('-32768,32767' returning smallint) as a(unlist_smallint_01)"
        
        # SQLSTATE = 22003 / ... / -numeric value is out of range:
        ,40100 : "select * from unlist('-32769' returning smallint) as a(unlist_smallint_02)"

        # SQLSTATE = 22003 / ... / -numeric value is out of range:
        ,40200 : "select * from unlist('32768' returning smallint) as a(unlist_smallint_03)"

        # time
        ,41000 : "select * from unlist('00:00:00.0000,23:59:59.9999' returning time) as a(unlist_time_01)"

        # SQLSTATE = 22018 / conversion error from string "00:00:00.10000"
        ,41200 : "select * from unlist('00:00:00.10000' returning time) as a(unlist_time_02)"

        # SQLSTATE = 22018 / conversion error from string "00"
        ,41300 : "select * from unlist('00:00:00.10000',':' returning time) as a(unlist_time_03)"

        # SQLSTATE = 22018 / conversion error from string "10000"
        ,41400 : "select * from unlist('00:00:00.10000','.' returning time) as a(unlist_time_04)"

        # must PASS:
        ,41500 : "select * from unlist('23:59:59' returning time) as a(unlist_time_05)"

        # time with time zone
        # ::: NB ::: here we do NOT specify name of time zone ==> value from 'set time zone' will be taken:
        ,42000 : "select * from unlist('00:00:00.0000,23:59:59.9999' returning time with time zone) as a(unlist_tmtz_01)"

        # SQLSTATE = 22018 / conversion error from string "00:00:00.10000"
        ,42100 : "select * from unlist('00:00:00.10000' returning time with time zone) as a(unlist_tmtz_02)"

        # SQLSTATE = 22018 / conversion error from string "00"
        ,42200 : "select * from unlist('00:00:00.10000',':' returning time with time zone) as a(unlist_tmtz_03)"

        # SQLSTATE = 22018 / conversion error from string "10000"
        ,42300 : "select * from unlist('00:00:00.10000','.' returning time with time zone) as a(unlist_tmtz_04)"

        # must PASS:
        ,42400 : "select * from unlist('23:59:59' returning time with time zone) as a(unlist_tmtz_05)"
        
        # must PASS:
        ,42500 : "select * from unlist('23:59:59.9999 europe/moscow,23:59:59.9999 -03:00,23:59:59.9999 gmt,23:59:59.9999 aet,23:59:59.9999 art,23:59:59.9999 etc/gmt+5,23:59:59.9999 america/kentucky/monticello' returning time with time zone) as a(unlist_tmtz_06)"

        # timestamp
        # must PASS:
        ,43000 : "select * from unlist('8/06/2315 00:00:00.0000,1245-12-01 23:59:59.9999' returning timestamp) as a(unlist_timestamp_01)"

        # SQLSTATE = 22018 / conversion error from string "00:00:00.0000,1245-12-01"
        ,43100 : "select * from unlist('8/06/2315 00:00:00.0000,1245-12-01 23:59:59.9999',' ' returning timestamp) as a(unlist_timestamp_02)"

        # SQLSTATE = 22018 / conversion error from string "8/06/2315"
        ,43200 : "select * from unlist('8/06/2315 00:00:00.0000,1245-12-01 23:59:59.9999',':' returning timestamp) as a(unlist_timestamp_03)"

        # SQLSTATE = 22018 / conversion error from string "00:00:00.0000"
        ,43300 : "select * from unlist('00:00:00.0000,23:59:59.9999' returning timestamp) as a(unlist_timestamp_04)"

        # timestamp with time zone
        # must PASS:
        ,43400 : "select * from unlist('8/06/2315 00:00:00.0000,1245-12-01 23:59:59.9999' returning timestamp with time zone) as a(unlist_tstz_01)"

        # conversion error from string "00:00:00.0000,1245-12-01"
        ,43500 : "select * from unlist('8/06/2315 00:00:00.0000,1245-12-01 23:59:59.9999',' ' returning timestamp with time zone) as a(unlist_tstz_02)"

        # conversion error from string "8/06/2315 00"
        ,43600 : "select * from unlist('8/06/2315 00:00:00.0000,1245-12-01 23:59:59.9999',':' returning timestamp with time zone) as a(unlist_tstz_03)"

        # conversion error from string "00:00:00.0000"
        ,43700 : "select * from unlist('00:00:00.0000,23:59:59.9999' returning timestamp with time zone) as a(unlist_tstz_04)"

        # must PASS:
        ,43800 : "select * from unlist('8/06/2315 23:59:59.9999 europe/moscow,8/06/2315 23:59:59.9999 -03:00,8/06/2315 23:59:59.9999 gmt,8/06/2315 23:59:59.9999 aet,8/06/2315 23:59:59.9999 art,8/06/2315 23:59:59.9999 etc/gmt+5,8/06/2315 23:59:59.9999 america/kentucky/monticello' returning timestamp with time zone) as a(unlist_tstz_05)"

        # varbinary(n)
        # must PASS:
        ,45000 : "select * from unlist('1111,12345678' returning varbinary(8)) as a(unlist_varbin_01)"
        # must PASS:
        ,45100 : "select * from unlist('text,texttext' returning varbinary(8)) as a(unlist_varbin_02)"

        # string right truncation / expected length 8, actual 12
        ,45200 : "select * from unlist('texttexttext' returning varbinary(8)) as a(unlist_varbin_03)"

        # token unknown / -)
        ,45300 : "select * from unlist('text' returning varbinary) as a(unlist_varbin_04)"

        # Positive value expected
        ,45400 : "select * from unlist('text' returning varbinary(0)) as a(unlist_varbin_05)"

        # blob
        # must PASS:
        ,50000 : "select * from unlist('1111,12345678,abcdefghijklmnopqrstuvwxyz' returning blob sub_type text) as a(unlist_blob_01)"
        # must PASS:
        ,50100 : "select * from unlist(0x13 || ',' || 0x14 returning blob sub_type binary) as a(unlist_blob_02)"

        # domain
        # must PASS:
        ,80000 : "select * from unlist('text,texttext,1243' returning test_domain) as a(unlist_domain_01)"
        # string right truncation / expected length 8, actual 12
        ,80000 : "select * from unlist('texttexttext' returning test_domain) as a(unlist_domain_02)"

        # token unknown / -)
        ,90000 : "select * from unlist('' returning ) as a"
    }

    with act.db.connect() as con:
        con.execute_immediate(f"set time zone '{SELECTED_TIMEZONE}'")
        con.commit()
        cur = con.cursor()
        for k, (q_idx, q_sttm) in enumerate(qry_map.items()):
            merge_output = []
            try:
                print(q_idx)
                print(q_sttm)
                cur.execute(q_sttm)
                cur_cols = cur.description
                for r in cur:
                    for i in range(0,len(cur_cols)):
                        if isinstance(r[i], bytes):
                            col_data = r[i].hex() # make value be in ISQL-form
                        else:
                            col_data = r[i]
                        print( cur_cols[i][0], ':', col_data )

            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                con.rollback()
            if k+1 < len(qry_map):
                print(DELIMITER_LINE)

    act.expected_stdout = f"""
        10000
        {qry_map[10000]}
        UNLIST_BIGINT_01 : -9223372036854775808
        UNLIST_BIGINT_01 : 9223372036854775807
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10100
        {qry_map[10100]}
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        (335544321, 335544916)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10150
        {qry_map[10150]}
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        (335544321, 335544916)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10200
        {qry_map[10200]}
        UNLIST_BOOLEAN_01 : True
        UNLIST_BOOLEAN_01 : False
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10250
        {qry_map[10250]}
        conversion error from string "right"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10300
        {qry_map[10300]}
        UNLIST_BINARY_01 : 3131313100000000
        UNLIST_BINARY_01 : 3132333435363738
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10350
        {qry_map[10350]}
        UNLIST_BINARY_02 : 7465787400000000
        UNLIST_BINARY_02 : 7465787474657874
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10400
        {qry_map[10400]}
        UNLIST_CHAR_01 : text
        UNLIST_CHAR_01 : texttext
        UNLIST_CHAR_01 : 1243
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10450
        {qry_map[10450]}
        arithmetic exception, numeric overflow, or string truncation
        -string right truncation
        -expected length 1, actual 4
        (335544321, 335544914, 335545033)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        10460
        {qry_map[10460]}
        Dynamic SQL Error
        -SQL error code = -842
        -Positive value expected
        -At line 1, column 44
        (335544569, 335544436, 335544712, 336397208)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        20000
        {qry_map[20000]}
        UNLIST_DATE_01 : 0001-01-01
        UNLIST_DATE_01 : 9999-12-31
        UNLIST_DATE_01 : 2315-08-06
        UNLIST_DATE_01 : 1245-12-01
        UNLIST_DATE_01 : 5555-12-28
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        20100
        {qry_map[20100]}
        value exceeds the range for valid dates
        (335544810,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        20200
        {qry_map[20200]}
        conversion error from string "1.01.10000"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        20300
        {qry_map[20300]}
        EXTRACT : 1
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        21000
        {qry_map[21000]}
        UNLIST_DECIMAL_01 : 4
        UNLIST_DECIMAL_01 : 2
        UNLIST_DECIMAL_01 : 5.83
        UNLIST_DECIMAL_01 : 23.01
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        21100
        {qry_map[21100]}
        UNLIST_DECIMAL_02 : 55555555555555555555555555555555555555
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        21200
        {qry_map[21200]}
        Dynamic SQL Error
        -SQL error code = -842
        -Precision must be from 1 to 38
        -At line 1, column 93
        (335544569, 335544436, 335545158, 336397208)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        22000
        {qry_map[22000]}
        UNLIST_DECFLOAT16_01 : 4
        UNLIST_DECFLOAT16_01 : 2.00
        UNLIST_DECFLOAT16_01 : 5.83
        UNLIST_DECFLOAT16_01 : 23.00000000000001
        UNLIST_DECFLOAT16_01 : 24.00000000000001
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        22100
        {qry_map[22100]}
        UNLIST_DECFLOAT34_01 : 4
        UNLIST_DECFLOAT34_01 : 2.00
        UNLIST_DECFLOAT34_01 : 5.83
        UNLIST_DECFLOAT34_01 : 23.00000000000001000000000000000001
        UNLIST_DECFLOAT34_01 : 24.00000000000001000000000000000001
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        25000
        {qry_map[25000]}
        UNLIST_DOUBLE_01 : 0.0
        UNLIST_DOUBLE_01 : -0.0
        UNLIST_DOUBLE_01 : 9.9e-307
        UNLIST_DOUBLE_01 : 1.7976931348623157e+308
        UNLIST_DOUBLE_01 : 4.0
        UNLIST_DOUBLE_01 : 2.0
        UNLIST_DOUBLE_01 : 5.83
        UNLIST_DOUBLE_01 : 23.00000000000001
        UNLIST_DOUBLE_01 : 24.000000000000007
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        27000
        {qry_map[27000]}
        UNLIST_FLOAT_01 : 4.0
        UNLIST_FLOAT_01 : 2.0
        UNLIST_FLOAT_01 : 5.829999923706055
        UNLIST_FLOAT_01 : 23.000001907348633
        UNLIST_FLOAT_01 : 24.000001907348633
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        30000
        {qry_map[30000]}
        UNLIST_INT_01 : -2147483648
        UNLIST_INT_01 : 2147483647
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        30100
        {qry_map[30100]}
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        (335544321, 335544916)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        30200
        {qry_map[30200]}
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        (335544321, 335544916)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        33000
        {qry_map[33000]}
        UNLIST_INT128_01 : -170141183460469231731687303715884105728
        UNLIST_INT128_01 : 170141183460469231731687303715884105727
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        33100
        {qry_map[33100]}
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        (335544321, 335544916)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        33200
        {qry_map[33200]}
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        (335544321, 335544916)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        35000
        {qry_map[35000]}
        UNLIST_NCHAR_01 : qwer
        UNLIST_NCHAR_01 : asdf
        UNLIST_NCHAR_01 : zxcv
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        35100
        {qry_map[35100]}
        arithmetic exception, numeric overflow, or string truncation
        -string right truncation
        -expected length 1, actual 4
        (335544321, 335544914, 335545033)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        35200
        {qry_map[35200]}
        Dynamic SQL Error
        -SQL error code = -842
        -Positive value expected
        -At line 1, column 45
        (335544569, 335544436, 335544712, 336397208)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        37000
        {qry_map[37000]}
        UNLIST_VARCHAR_01 : text
        UNLIST_VARCHAR_01 : texttext
        UNLIST_VARCHAR_01 : 1243
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        37100
        {qry_map[37100]}
        arithmetic exception, numeric overflow, or string truncation
        -string right truncation
        -expected length 8, actual 12
        (335544321, 335544914, 335545033)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        37200
        {qry_map[37200]}
        UNLIST_VARCHAR_03 : text
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        37300
        {qry_map[37300]}
        Dynamic SQL Error
        -SQL error code = -842
        -Positive value expected
        -At line 1, column 47
        (335544569, 335544436, 335544712, 336397208)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        38000
        {qry_map[38000]}
        UNLIST_NVARCHAR_01 : text
        UNLIST_NVARCHAR_01 : texttext
        UNLIST_NVARCHAR_01 : 1243
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        38100
        {qry_map[38100]}
        arithmetic exception, numeric overflow, or string truncation
        -string right truncation
        -expected length 8, actual 12
        (335544321, 335544914, 335545033)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        38200
        {qry_map[38200]}
        UNLIST_NVARCHAR_03 : text
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        38300
        {qry_map[38300]}
        Dynamic SQL Error
        -SQL error code = -842
        -Positive value expected
        -At line 1, column 53
        (335544569, 335544436, 335544712, 336397208)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        40000
        {qry_map[40000]}
        UNLIST_SMALLINT_01 : -32768
        UNLIST_SMALLINT_01 : 32767
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        40100
        {qry_map[40100]}
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        (335544321, 335544916)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        40200
        {qry_map[40200]}
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        (335544321, 335544916)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        41000
        {qry_map[41000]}
        UNLIST_TIME_01 : 00:00:00
        UNLIST_TIME_01 : 23:59:59.999900
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        41200
        {qry_map[41200]}
        conversion error from string "00:00:00.10000"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        41300
        {qry_map[41300]}
        conversion error from string "00"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        41400
        {qry_map[41400]}
        conversion error from string "10000"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        41500
        {qry_map[41500]}
        UNLIST_TIME_05 : 23:59:59
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        42000
        {qry_map[42000]}
        UNLIST_TMTZ_01 : 00:00:00
        UNLIST_TMTZ_01 : 23:59:59.999900
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        42100
        {qry_map[42100]}
        conversion error from string "00:00:00.10000"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        42200
        {qry_map[42200]}
        conversion error from string "00"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        42300
        {qry_map[42300]}
        conversion error from string "10000"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        42400
        {qry_map[42400]}
        UNLIST_TMTZ_05 : 23:59:59
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        42500
        {qry_map[42500]}
        UNLIST_TMTZ_06 : 23:59:59.999900
        UNLIST_TMTZ_06 : 23:59:59.999900-03:00
        UNLIST_TMTZ_06 : 23:59:59.999900
        UNLIST_TMTZ_06 : 23:59:59.999900
        UNLIST_TMTZ_06 : 23:59:59.999900
        UNLIST_TMTZ_06 : 23:59:59.999900
        UNLIST_TMTZ_06 : 23:59:59.999900
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43000
        {qry_map[43000]}
        UNLIST_TIMESTAMP_01 : 2315-08-06 00:00:00
        UNLIST_TIMESTAMP_01 : 1245-12-01 23:59:59.999900
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43100
        {qry_map[43100]}
        conversion error from string "00:00:00.0000,1245-12-01"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43200
        {qry_map[43200]}
        conversion error from string "8/06/2315 00"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43300
        {qry_map[43300]}
        conversion error from string "00:00:00.0000"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43400
        {qry_map[43400]}
        UNLIST_TSTZ_01 : 2315-08-06 00:00:00+06:30
        UNLIST_TSTZ_01 : 1245-12-01 23:59:59.999900+06:27:40
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43500
        {qry_map[43500]}
        conversion error from string "00:00:00.0000,1245-12-01"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43600
        {qry_map[43600]}
        conversion error from string "8/06/2315 00"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43700
        {qry_map[43700]}
        conversion error from string "00:00:00.0000"
        (335544334,)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        43800
        {qry_map[43800]}
        UNLIST_TSTZ_05 : 2315-08-06 23:59:59.999900+03:00
        UNLIST_TSTZ_05 : 2315-08-06 23:59:59.999900-03:00
        UNLIST_TSTZ_05 : 2315-08-06 23:59:59.999900+00:00
        UNLIST_TSTZ_05 : 2315-08-06 23:59:59.999900
        UNLIST_TSTZ_05 : 2315-08-06 23:59:59.999900
        UNLIST_TSTZ_05 : 2315-08-06 23:59:59.999900-05:00
        UNLIST_TSTZ_05 : 2315-08-06 23:59:59.999900-05:00
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        45000
        {qry_map[45000]}
        UNLIST_VARBIN_01 : 31313131
        UNLIST_VARBIN_01 : 3132333435363738
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        45100
        {qry_map[45100]}
        UNLIST_VARBIN_02 : 74657874
        UNLIST_VARBIN_02 : 7465787474657874
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        45200
        {qry_map[45200]}
        arithmetic exception, numeric overflow, or string truncation
        -string right truncation
        -expected length 8, actual 12
        (335544321, 335544914, 335545033)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        45300
        {qry_map[45300]}
        UNLIST_VARBIN_04 : 74657874
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        45400
        {qry_map[45400]}
        Dynamic SQL Error
        -SQL error code = -842
        -Positive value expected
        -At line 1, column 49
        (335544569, 335544436, 335544712, 336397208)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        50000
        {qry_map[50000]}
        UNLIST_BLOB_01 : 1111
        UNLIST_BLOB_01 : 12345678
        UNLIST_BLOB_01 : abcdefghijklmnopqrstuvwxyz
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        50100
        {qry_map[50100]}
        UNLIST_BLOB_02 : 3139
        UNLIST_BLOB_02 : 3230
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        80000
        {qry_map[80000]}
        arithmetic exception, numeric overflow, or string truncation
        -string right truncation
        -expected length 8, actual 12
        (335544321, 335544914, 335545033)
        -+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=-+=
        90000
        {qry_map[90000]}
        Dynamic SQL Error
        -SQL error code = -104
        -Token unknown - line 1, column 35
        -)
        (335544569, 335544436, 335544634, 335544382)
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
