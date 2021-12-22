#coding:utf-8
#
# PROGRAM/MODULE: firebird-qa
# FILE:           firebird/qa/fbtconv.py
# DESCRIPTION:    Utility to convert test from fbtest to pytest format
# CREATED:        27.4.2021
#
# The contents of this file are subject to the MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Copyright (c) 2021 Firebird Project (www.firebirdsql.org)
# All Rights Reserved.
#
# Contributor(s): Pavel Císař (original code)
#                 ______________________________________

"""firebird-qa - Utility to convert test from fbtest to pytest format


"""

from __future__ import annotations
from typing import Dict, List, Tuple
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
from operator import attrgetter
from packaging.version import Version, parse

PROG_NAME = 'fbt-convert'

DB_NEW            = 'New'
DB_EXISTING       = 'Existing'
DB_RESTORE        = 'Restore'
DB_ACCESS         = [None, DB_NEW, DB_EXISTING, DB_RESTORE]
CHARACTER_SETS    = [None, 'NONE','ASCII','BIG_5','CYRL','DOS437','DOS737','DOS775',
                    'DOS850','DOS852','DOS857','DOS858','DOS860','DOS861','DOS862',
                    'DOS863','DOS864','DOS865','DOS866','DOS869','EUCJ_0208','GBK',
                    'GB_2312','ISO8859_1','ISO8859_2','ISO8859_3','ISO8859_4',
                    'ISO8859_5','ISO8859_6','ISO8859_7','ISO8859_8','ISO8859_9',
                    'ISO8859_13','KOI8R','KOI8U','KSC_5601','NEXT','OCTETS',
                    'SJIS_0208','TIS620','UNICODE_FSS','UTF8','WIN1250','WIN1251',
                    'WIN1252','WIN1253','WIN1254','WIN1255','WIN1256','WIN1257',
                    'WIN1258','LATIN2']
PAGE_SIZES        = [None,'1024','2048','4096','8192','16384','32768']
TYPE_ISQL         = 'ISQL'
TYPE_PYTHON       = 'Python'
TEST_TYPES        = [TYPE_ISQL, TYPE_PYTHON]
PLATFORMS         = ['Windows','Linux','MacOS','FreeBSD','Solaris','HP-UX']
UNKNOWN           = 'Unknown'

tests = []

slow_tests = ['bugs.core_1544', 'bugs.core_3058']

def clean_last(txt: str) -> str:
    if not txt:
        return txt
    l = txt.splitlines()
    l[-1] = l[-1].strip()
    return '\n'.join(l)

class TestVersion:
    def __init__(self, id, platform, firebird_version, test_type,
                 test_script, database=DB_NEW, expected_stdout='', expected_stderr='',
                 database_name = None, backup_file = None, user_name='SYSDBA',
                 user_password='masterkey', database_character_set=None,
                 connection_character_set=None, page_size=None,
                 sql_dialect=3, init_script='', resources=None,
                 substitutions=None, qmid=None):
        self.id: str = id
        self.platform: str = platform
        self.firebird_version: Version = parse(firebird_version)
        self.test_type: str = test_type
        self.test_script: str = clean_last(test_script)
        self.database: str = database
        self.expected_stdout: str = clean_last('' if expected_stdout.strip() == '' else expected_stdout)
        self.expected_stderr: str = clean_last('' if expected_stderr.strip() == '' else expected_stderr)
        self.database_name: str = database_name
        self.backup_file: str = backup_file
        self.user_name: str = user_name
        self.user_password: str = user_password
        self.database_character_set: str = database_character_set
        self.connection_character_set: str = connection_character_set
        self.page_size: str = page_size
        self.sql_dialect: int = sql_dialect
        self.init_script: str = '' if init_script.strip() == '' else init_script
        self.resources: List[str] = None if resources is None else list(resources)
        self.substitutions: List[str] = substitutions if substitutions is not None else []
        self.qmid: str = qmid
        # Clean
    def escape(self, subs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return [tuple([a.replace('\\', '\\\\'), b.replace('\\', '\\\\')]) for a, b in subs]

class Test:
    def __init__(self,id,title='',description='',tracker_id='',min_versions=None,
                 versions=None,qmid=None):
        self.id: str = id
        self.title: str = title
        self.description: str = description
        self.tracker_id: str = tracker_id
        self.min_versions: List[str] = []
        if min_versions:
            self.min_versions.extend([parse(v.strip()) for v in min_versions.split(';')])
        self.qmid: str = qmid
        self.versions: List[TestVersion] = []
        #
        if versions:
            for i in versions:
                self.versions.append(TestVersion(id, **i))
            self.versions.sort(key=attrgetter('firebird_version'))
    def show(self):
        for attr in (a for a in dir(self) if not a.startswith('_')):
            if attr not in ('show'):
                print(f'{attr}={getattr(self,attr)}')

def multiline_comment(text: str, indent=15) -> str:
    result = []
    first = True
    for line in text.splitlines():
        if first:
            result.append(line)
            first = False
        else:
            result.append(f"#{' ' * indent}{line}")
    return '\n'.join(result)

def make_dirs(root: Path, path: Path):
    a = root
    for part in path.relative_to(root).parts:
        a = a / part
        if not a.is_dir():
            a.mkdir()
            init_py: Path = a / '__init__.py'
            init_py.write_text("# Python module\n")

def escape(txt: str) -> str:
    return txt.replace('\\', '\\\\')

def load_test(filename: Path, verbose: bool=False) -> Dict:
    if verbose:
        print(f"Loading {filename}...")
    expr_b = filename.read_bytes()
    expr = filename.read_text(encoding='utf-8')
    try:
        d = eval(expr)
    except SyntaxError:
        fix_expr = expr.replace('\\','\\\\')
        d = eval(fix_expr)
    return Test(**d)

def load_tests(path: Path, verbose: bool=False):
    dirlist = os.listdir(str(path))
    for dirname in (os.path.join(path, name) for name in dirlist
                    if os.path.isdir(os.path.join(path, name)) and not name.startswith('.')):
        load_tests(dirname, verbose=verbose)
    for testname in (name for name in dirlist if os.path.isfile(os.path.join(path, name)) and
                     os.path.splitext(name)[1].lower() == '.fbt'):
        tests.append(load_test(Path(path) / testname, verbose=verbose))

def clean_tests():
    v30: Version = parse('3.0')
    v40: Version = parse('4.0')
    for t in tests:
        new_versions = []
        last: Version = parse('0.1')
        has_30: bool = False
        t.id = t.id.replace('-','_')
        for v in t.versions:
            for mv in t.min_versions:
                if mv.major == v.firebird_version.major:
                    if mv > v.firebird_version:
                        v.firebird_version = mv
            #
            if (last < v.firebird_version) and (v.firebird_version < v30):
                last = v.firebird_version
            if v.firebird_version >= v30:
                has_30 = has_30 or v.firebird_version < v40
                new_versions.append(v)
        if not has_30:
            for v in t.versions:
                if v.firebird_version == last:
                    new_versions.insert(0, v)
        t.versions[:] = new_versions

def list_tests(root_path: Path, verbose: bool=False):
    for t in tests:
        test_file: Path = root_path / (t.id.replace('.', '/') + '.py')
        if not test_file.stem.endswith('_test'):
            test_file = test_file.with_name(test_file.stem + '_test.py')
        if verbose:
            print(f"id:         {t.id}")
            print(f"output:     {test_file}")
            print(f"versions:   {', '.join([str(v.firebird_version) for v in t.versions])}")
            print(f"type:       {t.versions[0].test_type}")
            print()
        else:
            print(f"{t.id} [{t.versions[0].test_type} {', '.join([str(v.firebird_version) for v in t.versions])}] to {test_file}")

def write_tests(root_path: Path, verbose: bool=False):
    if not root_path.is_dir():
        root_path.mkdir(parents=True)
        init_py: Path = root_path / '__init__.py'
        init_py.write_text("# Python module\n")
    for t in tests:
        test_file: Path = root_path / (t.id.replace('.', '/') + '.py')
        test_dir = test_file.parent
        if not test_dir.is_dir():
            make_dirs(root_path, test_dir)
        if test_file.name.startswith('core_'):
            if not test_file.stem.endswith('_test'):
                test_file = test_file.with_name(test_file.stem + '_test.py')
        else:
            if not test_file.name.startswith('test_'):
                test_file = test_file.with_name('test_' + test_file.name)
        if test_file.stem[0] in '0123456789':
            test_file = test_file.with_name('t' + test_file.name)
        content = f"""#coding:utf-8
#
# id:           {t.id}
# title:        {multiline_comment(escape(t.title))}
# decription:   {multiline_comment(escape(t.description))}
# tracker_id:   {t.tracker_id}
# min_versions: {[str(i) for i in t.min_versions]}
# versions:     {', '.join([str(v.firebird_version) for v in t.versions])}
# qmid:         {t.qmid}

import pytest
from firebird.qa import db_factory, {'isql_act' if t.versions[0].test_type == TYPE_ISQL else 'python_act'}, Action

"""
        # verbose output
        if verbose:
            print(f"Writing {t.id} to {test_file} [{t.versions[0].test_type} {', '.join([str(v.firebird_version) for v in t.versions])}]")
        # Write test versions
        seq = 0
        for v in t.versions:
            seq += 1
            content += f"# version: {v.firebird_version}\n"
            content += f"# resources: {v.resources}\n\n"
            subs = v.substitutions
            content += f'''substitutions_{seq} = {repr(subs)}\n\n'''
            content += f'''init_script_{seq} = """{escape(v.init_script)}"""\n\n'''
            #
            par = ''
            if v.database == 'New':
                if v.page_size is not None:
                    par = f"page_size={v.page_size}, "
                if v.database_character_set is not None:
                    par += f"charset='{v.database_character_set}', "
                if v.sql_dialect is not None:
                    par += f"sql_dialect={v.sql_dialect}, "
            elif v.database == 'Restore':
                par = f"from_backup='{v.backup_file}', "
            elif v.database == 'Existing':
                par = f"copy_of='{v.database_name}', "
            if v.database_name is not None:
                par += f"filename='{v.database_name}'"
            content += f"db_{seq} = db_factory({par}init=init_script_{seq})\n\n"
            if v.test_type == TYPE_ISQL:
                #
                content += f'''test_script_{seq} = """{escape(v.test_script)}"""\n\n'''
                content += f"act_{seq} = isql_act('db_{seq}', test_script_{seq}, substitutions=substitutions_{seq})\n\n"
                if v.expected_stdout:
                    sep = "'''" if v.expected_stdout.startswith('"') or v.expected_stdout.endswith('"') else '"""'
                    content += f'expected_stdout_{seq} = {sep}{escape(v.expected_stdout)}{sep}\n'
                if v.expected_stderr:
                    sep = "'''" if v.expected_stderr.startswith('"') or v.expected_stderr.endswith('"') else '"""'
                    content += f'expected_stderr_{seq} = {sep}{escape(v.expected_stderr)}{sep}\n'
                # Version specification
                if seq < len(t.versions):
                    ver_spec = f'>={str(v.firebird_version)},<{str(t.versions[seq].firebird_version)}'
                else:
                    ver_spec = f'>={str(v.firebird_version)}'
                content += f"""\n@pytest.mark.version('{ver_spec}')\n"""
                if v.platform != 'All':
                    content += f"""@pytest.mark.platform({", ".join([f"'{i}'" for i in v.platform.split(':')])})\n"""
                if v.id in slow_tests:
                    content += '@pytest.mark.slow\n'
                content += f"""def test_{seq}(act_{seq}: Action):\n"""
                if v.expected_stdout:
                    content += f'    act_{seq}.expected_stdout = expected_stdout_{seq}\n'
                if v.expected_stderr:
                    sep = "'''" if v.expected_stderr.startswith('"') or v.expected_stderr.endswith('"') else '"""'
                    content += f'    act_{seq}.expected_stderr = expected_stderr_{seq}\n'
                content += f'    act_{seq}.execute()\n'
                if v.expected_stderr:
                    content += f'    assert act_{seq}.clean_stderr == act_{seq}.clean_expected_stderr\n'
                if v.expected_stdout:
                    if v.expected_stderr:
                        content += '\n'
                    content += f'    assert act_{seq}.clean_stdout == act_{seq}.clean_expected_stdout\n'
                content += '\n'
            elif v.test_type == TYPE_PYTHON:
                #
                content += f'''# test_script_{seq}\n#---\n# {multiline_comment(escape(v.test_script), 2)}\n#---\n'''
                content += f"act_{seq} = python_act('db_{seq}', substitutions=substitutions_{seq})\n\n"
                if v.expected_stderr:
                    sep = "'''" if v.expected_stderr.startswith('"') or v.expected_stderr.endswith('"') else '"""'
                    content += f'expected_stderr_{seq} = {sep}{escape(v.expected_stderr)}{sep}\n'
                if v.expected_stdout:
                    if v.expected_stderr:
                        content += '\n'
                    sep = "'''" if v.expected_stdout.startswith('"') or v.expected_stdout.endswith('"') else '"""'
                    content += f'expected_stdout_{seq} = {sep}{escape(v.expected_stdout)}{sep}\n'
                # Version specification
                if seq < len(t.versions):
                    ver_spec = f'>={str(v.firebird_version)},<{str(t.versions[seq].firebird_version)}'
                else:
                    ver_spec = f'>={str(v.firebird_version)}'
                content += f"""\n@pytest.mark.version('{ver_spec}')\n"""
                if v.platform != 'All':
                    content += f"""@pytest.mark.platform({", ".join([f"'{i}'" for i in v.platform.split(':')])})\n"""
                #content += "@pytest.mark.xfail\n"
                content += f"""def test_{seq}(act_{seq}: Action):\n    pytest.fail("Test not IMPLEMENTED")\n\n"""
                content += '\n'

        #
        test_file.write_text(content)

def main():
    """Utility to convert test from fbtest to pytest format.
    """
    parser: ArgumentParser = ArgumentParser(PROG_NAME, description=main.__doc__,
                                            formatter_class=ArgumentDefaultsHelpFormatter)
    #
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    parser.add_argument('-o', '--output', help="Output directory")
    parser.add_argument('source', help="Source directory or file")

    args = parser.parse_args()
    #
    src = Path(args.source)
    if src.is_dir():
        load_tests(src, verbose=args.verbose)
    elif src.is_file():
        tests.append(load_test(src, verbose=args.verbose))
    else:
        parser.exit(message="Source not found")
    clean_tests()
    if args.output:
        write_tests(Path(args.output), verbose=args.verbose)
    else:
        list_tests(Path('.'), verbose=args.verbose)

if __name__ == '__main__':
    main()
