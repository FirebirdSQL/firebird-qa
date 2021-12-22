#coding:utf-8
#
# id:           functional.database.alter.03
# title:        Alter database: add file with name of this database or previously added files must fail
# decription:   Add same file twice must fail
# tracker_id:
# min_versions: []
# versions:     3.0
# qmid:

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DatabaseError

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# cursor=db_conn.cursor()
#  cursor.execute("ALTER DATABASE ADD FILE '$(DATABASE_LOCATION)TEST.G00' STARTING 10000")
#  db_conn.commit()
#  try:
#    cursor=db_conn.cursor()
#    cursor.execute("ALTER DATABASE ADD FILE '$(DATABASE_LOCATION)TEST.G00' STARTING 20000")
#    db_conn.commit()
#  except kdb.DatabaseError, e:
#    print (e[0])
#  except:
#    print ("Unexpected exception",sys.exc_info()[0])
#    print ("Arguments",sys.exc_info()[1])
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, capsys):
    with act_1.db.connect() as con:
        with con.cursor() as c:
            c.execute(f"ALTER DATABASE ADD FILE '{act_1.db.db_path.with_name('TEST.G00')}' STARTING 10000")
            con.commit()
            with pytest.raises(DatabaseError, match='.*Cannot add file with the same name as the database or added files.*'):
                c.execute(f"ALTER DATABASE ADD FILE '{act_1.db.db_path.with_name('TEST.G00')}' STARTING 20000")
    # Passed
