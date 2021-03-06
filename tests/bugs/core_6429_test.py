#coding:utf-8
#
# id:           bugs.core_6429
# title:        Timezone offset in timestamp/time literal, CAST, SET TIME ZONE and AT TIME ZONE should follow SQL standard syntax only
# decription:   
#                  Test verifies miscelaneous forms of OFFSET for timezone part.
#                  According to note by Adriano (see ticket), values that represent HOURS and MINUTES, *can* be written in single-character form,
#                  i.e. 'H' and 'M' (rather than form 'HH' and 'MM' which was proposed by Mark).
#                  It looks srange but currently offset parts can be written with leading (non-valuable) zeroes.
#               
#                  Checked on 4.0.0.2240.
#                
# tracker_id:   CORE-6429
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;


    -- ##################################  CHECK SET TIME ZONE ############################################

    set time zone '-0:0'; -- must pass

    set time zone '-00:00'; -- must pass

    set time zone '+0:0'; -- must pass

    set time zone '+00:00'; -- must pass

    -- Despite on very strange view, these statements all pass:
    set time zone '+0: 0';

    set time zone '-	0:				0';

    set time zone '	+	0	:	0	';

    -- Also passes!
    set time zone '	+	0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001	:	00001	';


    -- All following must fail:
    set time zone '';

    set time zone ' ';

    set time zone '	'; -- TAB

    -- CR/LF
    set time zone '
    ';

    set time zone '00:00';

    set time zone '0:0';


    set time zone '+14:01'; -- must fail with "use format +/-hours:minutes and be between -14:00 and +14:00"

    set time zone '-14:01'; -- must fail with "use format +/-hours:minutes and be between -14:00 and +14:00"

    set time zone '	-0: -0';  -- must fail with "use format +/-hours:minutes and be between -14:00 and +14:00"

    set time zone '-0:0:';  -- must fail with "use format +/-hours:minutes and be between -14:00 and +14:00"

    set time zone '-0:+0';  -- must fail with "use format +/-hours:minutes and be between -14:00 and +14:00"

    set time zone '-0: +0';  -- must fail with "use format +/-hours:minutes and be between -14:00 and +14:00"

    set time zone '-0:0.0';  -- must fail with "use format +/-hours:minutes and be between -14:00 and +14:00"

    set time zone '+00:00.0';  -- must fail with "use format +/-hours:minutes and be between -14:00 and +14:00"

    -- #########################  CHECK TIMEZONE OFFSET IN TIMESTAMP LITERALS  ##########################

    select timestamp '2018-01-02 02:02:02.2222 -03:00' from rdb$database; -- must pass

    select timestamp '2018-01-02 02:02:02.2222 -3:0' from rdb$database;

    select timestamp '2018-01-02 02:02:02.2222 -14:0' from rdb$database;

    select timestamp '2018-01-02 02:02:02.2222 +14:0' from rdb$database;

    -- also PASSES!
    select timestamp '2018-01-02 02:02:02.2222 +0000000000000000000000000000014			:			00000000000000000000000000000000000000000000000000000000000' from rdb$database;


    select timestamp '2018-01-02 02:02:02.2222 +	0:	0' from rdb$database;

    select timestamp '2018-01-02 02:02:02.2222				-	0		:	0		' from rdb$database;

    -- Must fail:
    -- Statement failed, SQLSTATE = 22009 / Invalid time zone region
    select timestamp '2018-01-02 02:02:02.2222				0		:	0		' from rdb$database;

    select timestamp '2018-01-02 02:02:02.2222 11:1' from rdb$database;

    -- #########################  CHECK TIMEZONE OFFSET IN TIME LITERALS  ##########################


    select time '03:03:03.3333 -03:00' from rdb$database; -- must pass

    select time '03:03:03.3333 -3:0' from rdb$database;

    select time '03:03:03.3333 -14:0' from rdb$database;

    select time '03:03:03.3333 +14:0' from rdb$database;

    -- also PASSES!
    select time '03:03:03.3333 +0000000000000000000000000000014			:			00000000000000000000000000000000000000000000000000000000000' from rdb$database;


    select time '03:03:03.3333 +	0:	0' from rdb$database;

    select time '03:03:03.3333				-	0		:	0		' from rdb$database;

    -- Must fail:
    -- Statement failed, SQLSTATE = 22009 / Invalid time zone region
    select time '03:03:03.3333				0		:	0		' from rdb$database;

    select time '03:03:03.3333 11:1' from rdb$database;

    -- #########################  CHECK CAST TO TIMESTAMP LITERALS WITH TIMEZONE  ##########################

    select cast( '2018-01-02 04:04:04.4444 -03:00' as timestamp with time zone) from rdb$database; -- must pass

    select cast( '2018-01-02 04:04:04.4444 -3:0' as timestamp with time zone) from rdb$database;

    select cast( '2018-01-02 04:04:04.4444 -14:0' as timestamp with time zone) from rdb$database;

    select cast( '2018-01-02 04:04:04.4444 +14:0' as timestamp with time zone) from rdb$database;

    -- also PASSES!
    select cast( '2018-01-02 04:04:04.4444 +0000000000000000000000000000014			:			00000000000000000000000000000000000000000000000000000000000' as timestamp with time zone) from rdb$database;


    select cast( '2018-01-02 04:04:04.4444 +	0:	0' as timestamp with time zone) from rdb$database;

    select cast( '2018-01-02 04:04:04.4444				-	0		:	0		' as timestamp with time zone) from rdb$database;

    -- Must fail:
    -- Statement failed, SQLSTATE = 22009 / Invalid time zone region
    select cast( '2018-01-02 04:04:04.4444				0		:	0		' as timestamp with time zone) from rdb$database;

    select cast( '2018-01-02 04:04:04.4444 11:1' as timestamp with time zone) from rdb$database;

    -- #########################  CHECK IMPLICIT CAST WITH USING 'AT TIME ZONE'  ##########################

    select time '05:05:05.5555' at time zone '-03:00' from rdb$database; -- must pass

    select time '05:05:05.5555' at time zone '-3:0' from rdb$database;

    select time '05:05:05.5555' at time zone '-14:0' from rdb$database;

    select time '05:05:05.5555' at time zone '+14:0' from rdb$database;

    -- also PASSES!
    select time '05:05:05.5555' at time zone '+0000000000000000000000000000014			:			00000000000000000000000000000000000000000000000000000000000' from rdb$database;


    select time '05:05:05.5555' at time zone '+	0:	0' from rdb$database;

    select time '05:05:05.5555'	at time zone '			-	0		:	0		' from rdb$database;

    -- Must fail:
    -- Statement failed, SQLSTATE = 22009 / Invalid time zone region
    select time '05:05:05.5555' at time zone	'			0		:	0		' from rdb$database;

    select time '05:05:05.5555' at time zone '11:1' from rdb$database;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    2018-01-02 02:02:02.2222 -03:00                           


    2018-01-02 02:02:02.2222 -03:00                           


    2018-01-02 02:02:02.2222 -14:00                           


    2018-01-02 02:02:02.2222 +14:00                           


    2018-01-02 02:02:02.2222 +14:00                           


    2018-01-02 02:02:02.2222 +00:00                           


    2018-01-02 02:02:02.2222 +00:00                           


    03:03:03.3333 -03:00                           


    03:03:03.3333 -03:00                           


    03:03:03.3333 -14:00                           


    03:03:03.3333 +14:00                           


    03:03:03.3333 +14:00                           


    03:03:03.3333 +00:00                           


    03:03:03.3333 +00:00                           


    2018-01-02 04:04:04.4444 -03:00                           


    2018-01-02 04:04:04.4444 -03:00                           


    2018-01-02 04:04:04.4444 -14:00                           


    2018-01-02 04:04:04.4444 +14:00                           


    2018-01-02 04:04:04.4444 +14:00                           


    2018-01-02 04:04:04.4444 +00:00                           


    2018-01-02 04:04:04.4444 +00:00                           




    01:04:05.5555 -03:00                           


    01:04:05.5555 -03:00                           


    14:04:05.5555 -14:00                           


    18:04:05.5555 +14:00                           


    18:04:05.5555 +14:00                           


    04:04:05.5555 +00:00                           


    04:04:05.5555 +00:00                           

  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 
        

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 00:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 0:0

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: +14:01 - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: -14:01 - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: 	-0: -0 - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: -0:0: - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: -0:+0 - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: -0: +0 - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: -0:0.0 - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone offset: +00:00.0 - must use format +/-hours:minutes and be between -14:00 and +14:00

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 0		:	0		

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 11:1

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 0		:	0		

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 11:1

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 0		:	0		

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 11:1

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 0		:	0		

    Statement failed, SQLSTATE = 22009
    Invalid time zone region: 11:1
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

