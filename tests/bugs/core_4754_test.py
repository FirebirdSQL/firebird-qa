#coding:utf-8

"""
ID:          issue-5058
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/5058
TITLE:       Bugcheck 167 (invalid SEND request) while working with GTT from several attachments (using EXECUTE STATEMENT ... ON EXTERNAL and different roles)
DESCRIPTION:
JIRA:        CORE-4754
FBTEST:      bugs.core_4754
NOTES:
    [13.04.2026] pzotov
    Refactored. Verify outcome for all possible types of indices: regular, computed and [in 5x+] partial.
    Checked on 6.0.0.1891; 5.0.4.1808; 4.0.7.3269; 3.0.14.33855.
"""

import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, TraAccessMode, DatabaseError

GTT_TABLE_NAME = 'gtt_session'
init_script = f"""
    recreate global temporary table {GTT_TABLE_NAME}(x int, y int) on commit preserve rows;
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db')

@pytest.mark.version('>=3')
def test_1(act: Action, capsys):
    custom_tpb = tpb(isolation=Isolation.READ_COMMITTED_RECORD_VERSION,
                     access_mode=TraAccessMode.WRITE, lock_timeout=0)
    IDX_TYPES = ['regular', 'computed']
    if act.is_version('<5'):
         pass
    else:
        IDX_TYPES.append('partial',)

    for i_type in IDX_TYPES:
        with act.db.connect() as con1:
            tx1a = con1.transaction_manager(custom_tpb)
            cu1a = tx1a.cursor()
            tx1b = con1.transaction_manager(custom_tpb)
            cu1b = tx1b.cursor()
            try:
                cu1a.execute(f"insert into {GTT_TABLE_NAME} select rand()*10, rand()*10 from rdb$types")

                if i_type == 'regular':
                    idx_ddl = f"create index {GTT_TABLE_NAME}_x_y on {GTT_TABLE_NAME} (x,y)"
                elif i_type == 'computed':
                    idx_ddl = f"create index {GTT_TABLE_NAME}_x_y on {GTT_TABLE_NAME} computed by (x+y)"
                elif i_type == 'partial':
                    idx_ddl = f"create descending index {GTT_TABLE_NAME}_x_y on {GTT_TABLE_NAME} (y,x) where y > 5"
                else:
                    assert False, f'Wrong / unknown index type specified: {i_type}'

                #cur2.execute(f"create index {GTT_TABLE_NAME}_x_y on {GTT_TABLE_NAME} computed by (x+y)")
                cu1b.execute(f"create index {GTT_TABLE_NAME}_x_y on {GTT_TABLE_NAME} (x,y)")

                # WI-V2.5.6.27013 issues here:
                # lock conflict on no wait transaction
                # unsuccessful metadata update object
                # TABLE "..." is in use / -901 / 335544345
                tx1b.commit()

                tx1a.commit()
                print('Exception unexpectedly DID NOT raise.')
                
                # Control here must NOT pass at all:
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                with act.db.connect() as con2:
                    tx2 = con2.transaction_manager(custom_tpb)
                    cu2 = tx2.cursor()
                    try:
                        # Following INSERT statement caused exception on WI-V2.5.4.26856:
                        # fdb.fbcore.DatabaseError: ('Error while executing SQL statement:\n- SQLCODE: -902\n- internal Firebird consistency
                        # check (invalid SEND request (167), file: exe.cpp line: 614)', -902, 335544333)
                        #
                        cu2.execute( f"insert into {GTT_TABLE_NAME} select rand()*11, rand()*11 from rdb$types" )
                        tx2.commit()
                    except DatabaseError as x:
                        print(f'Failed to add rows in con2:')
                        print(x.__str__())
                        print(x.gds_codes)
                    
            except DatabaseError as e:
                print(f'Checked index type: {i_type}')
                print(e.__str__())
                print(e.gds_codes)

        expected_stdout_5x = f"""
            Checked index type: {i_type}
            lock conflict on no wait transaction
            -unsuccessful metadata update
            -object TABLE "{GTT_TABLE_NAME.upper()}" is in use
            (335544345, 335544351, 335544453)
        """

        expected_stdout_6x = f"""
            Checked index type: {i_type}
            unsuccessful metadata update
            -CREATE INDEX "PUBLIC"."{GTT_TABLE_NAME.upper()}_X_Y" failed
            -lock conflict on no wait transaction
            -unsuccessful metadata update
            -object TABLE "PUBLIC"."{GTT_TABLE_NAME.upper()}" is in use
            (335544351, 336397316, 335544345, 335544351, 335544453)
        """
        
        act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()
