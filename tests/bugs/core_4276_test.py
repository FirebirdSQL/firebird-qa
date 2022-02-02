#coding:utf-8

"""
ID:          issue-4600
ISSUE:       4600
TITLE:       Error on create table with "CHARACTER SET DOS775" field
DESCRIPTION:
JIRA:        CORE-4276
FBTEST:      bugs.core_4276
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('BLOB_CONTENT.*', '')])

test_script = """
    recreate table "ĄČĘĢÆĖŠŚÖÜØ£"(
            "ąčęėįšųūž" varchar(50) character set dos775
            ,"Õisu ja kariste järved" blob sub_type 1 character set dos775
    );
    commit;
    show table;
    show table "ĄČĘĢÆĖŠŚÖÜØ£";
    insert into "ĄČĘĢÆĖŠŚÖÜØ£"("ąčęėįšųūž", "Õisu ja kariste järved")
    values(
            'ÓßŌŃõÕµńĶķĻļņĒŅ',
            'Green - viens no trim primārās krāsas, zaļā tiek uzskatīts diapazontsvetov spektrs ar viļņa
            garumu aptuveni 500-565 nanometri. Sistēma CMYK druka zaļā iegūst, sajaucot dzelteno un
            zilganzaļi (cyan).Dabā, Catalpa - zaļa augs.
            Krāsu zaļie augi ir dabiski, ka cilvēks etalonomzeleni.
            Zaļā koku varde.
            Ir plaši izplatīti dabā. Lielākā daļa augu ir zaļā krāsā, jo tie satur pigmentu fotosintēzes -
            hlorofilu (hlorofils absorbē lielu daļu no sarkano stariem saules spektra, atstājot uztveri
            atstarotās un filtrē zaļā krāsā). Dzīvnieki ar zaļo krāsu tā izmantošanu maskēties fona augiem.'
    );
    set list on;
    set blob all;
    select "ąčęėįšųūž", "Õisu ja kariste järved" as blob_content
    from "ĄČĘĢÆĖŠŚÖÜØ£";
"""

expected_stdout = """
					   ĄČĘĢÆĖŠŚÖÜØ£
	ąčęėįšųūž                       VARCHAR(50) CHARACTER SET DOS775 Nullable
	Õisu ja kariste järved          BLOB segment 80, subtype TEXT CHARACTER SET DOS775 Nullable

	ąčęėįšųūž                       ÓßŌŃõÕµńĶķĻļņĒŅ
	BLOB_CONTENT                    80:0
	Green - viens no trim primārās krāsas, zaļā tiek uzskatīts diapazontsvetov spektrs ar viļņa
	garumu aptuveni 500-565 nanometri. Sistēma CMYK druka zaļā iegūst, sajaucot dzelteno un
	zilganzaļi (cyan).Dabā, Catalpa - zaļa augs.
	Krāsu zaļie augi ir dabiski, ka cilvēks etalonomzeleni.
	Zaļā koku varde.
	Ir plaši izplatīti dabā. Lielākā daļa augu ir zaļā krāsā, jo tie satur pigmentu fotosintēzes -
	hlorofilu (hlorofils absorbē lielu daļu no sarkano stariem saules spektra, atstājot uztveri
	atstarotās un filtrē zaļā krāsā). Dzīvnieki ar zaļo krāsu tā izmantošanu maskēties fona augiem.
"""

script_file = temp_file('test-script.sql')

@pytest.mark.version('>=3')
def test_1(act: Action, script_file: Path):
    script_file.write_text(test_script, encoding='cp775')
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q', '-b'], input_file=script_file, charset='DOS775')
    assert act.clean_stdout == act.clean_expected_stdout
