#coding:utf-8
#
# id:           bugs.core_1689
# title:        'There are <n> dependencies' error message shows the wrong count of dependent objects.
# decription:   
#                   For FB 2.5 and 3.x - this test uses UDF from ib_udf.
#               
#                   24.01.2019. 
#                   Added separate code for running on FB 3.0.x because its current STDERR now differ from old one.
#               
#                   Added separate code for running on FB 4.0.x.
#                   UDF usage is deprecated in FB 4+, see: ".../doc/README.incompatibilities.3to4.txt".
#                   Functions div, frac, dow, sdow, getExactTimestampUTC and isLeapYear got safe replacement 
#                   in UDR library "udf_compat", see it in folder: ../plugins/udr/
#               
#                   Checked on:
#                       2.5.9.27126: OK, 0.719s.
#                       3.0.5.33086: OK, 1.734s.
#                       4.0.0.1340: OK, 3.078s.
#                       4.0.0.1378: OK, 3.234s.
#               
#                   NOTE. Build 4.0.0.1172 (date: 25.08.2018) raises here exception with 'UDF' instead 'Function' in STDERR.
#                 
# tracker_id:   CORE-1689
# min_versions: ['2.5.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    declare external function UDF30_getExactTimestamp
      timestamp
      returns parameter 1
      entry_point 'getExactTimestamp' module_name 'fbudf'^

    create table t(a int)^
    create trigger tad for t after delete as declare dummy timestamp; begin dummy = UDF30_getExactTimestamp(); end^
    create view vudf(t) as select UDF30_getExactTimestamp() from rdb$database^
    create table tudf(a int, c computed by(UDF30_getExactTimestamp()))^
    create domain dud int check(value between extract(week from UDF30_getExactTimestamp()) and 25)^
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    drop external function UDF30_getExactTimestamp;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 38000
    unsuccessful metadata update
    -cannot delete
    -Function UDF30_GETEXACTTIMESTAMP
    -there are 4 dependencies
  """

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

# version: 4.0
# resources: None

substitutions_2 = []

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    -- See declaration sample in plugins\\udr\\UdfBackwardCompatibility.sql:
    set bail on;
    create function UDR40_getExactTimestampUTC
    returns timestamp
    external name 'udf_compat!UC_getExactTimestampUTC'
    engine udr;
   
    create table test_dts(
        id int, 
        dts timestamp check ( datediff(minute from dts to UDR40_getExactTimestampUTC()) < 5 ) 
    );
    commit;
    
    set term ^;
    create trigger trg_test_dts_ad for test_dts after delete as
        declare dummy timestamp; 
    begin 
        dummy = UDR40_getExactTimestampUTC(); 
    end
    ^
    set term ;^
    commit;
    

    
    create view v_test as 
    select UDR40_getExactTimestampUTC() as UTC_stamp  -- rdb$N, dep_type=3
    from rdb$database
    ;
    
    
    create table test_udr(a int, c computed by( UDR40_getExactTimestampUTC() )) -- rdb$N, dep_type=3
    ;
   
    create domain dm_test int check(value between extract(week from UDR40_getExactTimestampUTC() ) and 25) ;
    
    commit;

    drop function UDR40_getExactTimestampUTC;

    /*
    set count on;
    set list on;
    select rd.rdb$dependent_name, rd.rdb$dependent_type
    from rdb$dependencies rd
    where rd.rdb$depended_on_name = upper('UDR40_GETEXACTTIMESTAMPUTC')
    order by rd.rdb$dependent_name
    ;
    */
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stderr_2 = """
    Statement failed, SQLSTATE = 38000
    unsuccessful metadata update
    -cannot delete
    -Function UDR40_GETEXACTTIMESTAMPUTC
    -there are 6 dependencies
  """

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_expected_stderr == act_2.clean_stderr

