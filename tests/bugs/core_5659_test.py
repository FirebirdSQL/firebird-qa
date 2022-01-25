#coding:utf-8

"""
ID:          issue-5925
ISSUE:       5925
TITLE:       Bad PLAN generated for query on Firebird v3.0
DESCRIPTION:
  Test is based on data from original database that was provided in the ticket by its author.
  Lot of data from tables were removed in order to reduce DB size.
JIRA:        CORE-5659
"""

import pytest
import zipfile
from pathlib import Path
from firebird.qa import *

db = db_factory()

act_1 = python_act('db')

expected_stdout = """
    PLAN JOIN (B INDEX (COM_PEDIDO_IDX1), A INDEX (FK_COM_PEDIDO_ITEM_PEDIDO), C INDEX (PK_EST_PRODUTO))
"""

test_script = """
    set planonly;
    select
        a.id_pedido_item,
        c.descricao
    from com_pedido b
    join com_pedido_item a on a.id_pedido = b.id_pedido
                    and ( not(a.id_produto =1 and a.id_pedido_item_pai is not null))
    join est_produto c on c.id_produto = a.id_produto
    where
        -- b.dth_pedido between cast('10.12.16 05:00:00' as timestamp) and cast('10.12.16 20:00:00' as timestamp)
        b.dth_pedido between ? and ? ;
"""

fbk_file = temp_file('core5637-security3.fbk')
fdb_file = temp_file('bad_plan_5659.fdb')

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, fbk_file: Path, fdb_file: Path):
    zipped_fbk_file = zipfile.Path(act_1.files_dir / 'core_5659.zip', at='core_5659.fbk')
    fbk_file.write_bytes(zipped_fbk_file.read_bytes())
    #
    with act_1.connect_server() as srv:
        srv.database.restore(backup=fbk_file, database=fdb_file)
        srv.wait()
    #
    act_1.expected_stdout = expected_stdout
    act_1.isql(switches=['-q', act_1.get_dsn(fdb_file)], input=test_script, connect_db=False)
    assert act_1.clean_stdout == act_1.clean_expected_stdout
