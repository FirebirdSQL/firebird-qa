#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/812413420e110cb77cdd9688b888f5e1ff9e3d1e
TITLE:       Allow all users to query constants from SYSTEM packages
DESCRIPTION:
NOTES:
    [05.07.2026] pzotov
    Confirmed problem on 6.0.0.1948-20260513_212500-f8eee95, got:
        firebird.driver.types.DatabaseError: no permission for USAGE access to PACKAGE "SYSTEM"."RDB$BLOB_UTIL"
        -Effective user is ...
    Checked on 6.0.0.2052.
"""
import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db')
tmp_user = user_factory('db', name='tmp_81241342_junior', password='123')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_user: User):

    with act.db.connect(user = tmp_user.name, password = tmp_user.password) as con:
        cur = con.cursor()
        cur.execute(
            """
            select
                system.rdb$blob_util.from_begin
                ,system.rdb$blob_util.from_current
                ,system.rdb$blob_util.from_end
            from rdb$database
            """
        )
        # Following must no raise any error:
        for r in cur:
            pass
