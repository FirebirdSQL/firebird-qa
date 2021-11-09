#coding:utf-8
#
# PROGRAM/MODULE: firebird-qa
# FILE:           firebird/qa/plugin.py
# DESCRIPTION:    pytest plugin for Firebird QA
# CREATED:        9.4.2021
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
# Copyright (c) 2020 Firebird Project (www.firebirdsql.org)
# All Rights Reserved.
#
# Contributor(s): Pavel Císař (original code)
#                 ______________________________________

"""firebird-qa - pytest plugin for Firebird QA


"""

from __future__ import annotations
from typing import List, Dict
import os
import re
import shutil
import platform
import difflib
import pytest
from _pytest.fixtures import FixtureRequest
from subprocess import run, CompletedProcess
from pathlib import Path
#from configparser import ConfigParser, ExtendedInterpolation
from packaging.specifiers import SpecifierSet
from packaging.version import parse
from firebird.driver import connect, connect_server, create_database, driver_config, \
     NetProtocol, Server, CHARSET_MAP

_vars_ = {'server': None,
          'bin-dir': None,
          'firebird-config': None,
          'runslow': False,
          }

_platform = platform.system()

def pytest_addoption(parser, pluginmanager):
    ""
    grp = parser.getgroup('firebird', "Firebird server", 'general')
    grp.addoption('--server', help="Server configuration name", default='')
    grp.addoption('--bin-dir', metavar='PATH', help="Path to directory with Firebird utilities")
    grp.addoption('--protocol',
                  choices=[i.name.lower() for i in NetProtocol],
                  help="Network protocol used for database attachments")
    grp.addoption('--runslow', action='store_true', default=False, help="Run slow tests")
    grp.addoption('--save-output', action='store_true', default=False, help="Save test std[out|err] output to files")

def pytest_report_header(config):
    return ["Firebird:",
            f"  root: {_vars_['root']}",
            f"  databases: {_vars_['databases']}",
            f"  backups: {_vars_['backups']}",
            f"  driver configuration: {_vars_['firebird-config']}",
            f"  server: {_vars_['server']}",
            f"  protocol: {_vars_['protocol']}",
            f"  engine: v{_vars_['version']}, {_vars_['arch']}",
            f"  home: {_vars_['home-dir']}",
            f"  bin: {_vars_['bin-dir']}",
            f"  security db: {_vars_['security-db']}",
            f"  run slow test: {_vars_['runslow']}",
            f"  save test output: {_vars_['save-output']}",
            ]

def set_tool(tool: str):
    path: Path = _vars_['bin-dir'] / tool
    if not path.is_file():
        path = path.with_suffix('.exe')
        if not path.is_file():
            pytest.exit(f"Can't find '{tool}' in {_vars_['bin-dir']}")
    _vars_[tool] = path

def pytest_configure(config):
    # pytest.ini
    config.addinivalue_line(
        "markers", "version(versions): Firebird version specifications"
    )
    config.addinivalue_line(
        "markers", "platform(platforms): Platform names"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow to run"
    )
    if config.getoption('help'):
        return
    config_path: Path = Path.cwd() / 'firebird-driver.conf'
    if config_path.is_file():
        driver_config.read(str(config_path))
        _vars_['firebird-config'] = config_path
    driver_config.register_database('pytest')
    #
    _vars_['basetemp'] = config.getoption('basetemp')
    _vars_['runslow'] = config.getoption('runslow')
    _vars_['root'] = config.rootpath
    path = config.rootpath / 'databases'
    _vars_['databases'] = path if path.is_dir() else config.rootpath
    path = config.rootpath / 'backups'
    _vars_['backups'] = path if path.is_dir() else config.rootpath
    _vars_['server'] = config.getoption('server')
    _vars_['protocol'] = config.getoption('protocol')
    _vars_['save-output'] = config.getoption('save_output')
    srv_conf = driver_config.get_server(_vars_['server'])
    _vars_['host'] = srv_conf.host.value if srv_conf is not None else ''
    _vars_['password'] = srv_conf.password.value
    #
    with connect_server(_vars_['server'], user='SYSDBA',
                        password=_vars_['password']) as srv:
        _vars_['version'] = parse(srv.info.version.replace('-dev', ''))
        _vars_['home-dir'] = Path(srv.info.home_directory)
        if bindir := config.getoption('bin_dir'):
            _vars_['bin-dir'] = Path(bindir)
        else:
            bindir = _vars_['home-dir'] / 'bin'
            if not bindir.exists():
                bindir = _vars_['home-dir']
            _vars_['bin-dir'] = bindir
        _vars_['lock-dir'] = Path(srv.info.lock_directory)
        _vars_['bin-dir'] = Path(bindir) if bindir else _vars_['home-dir']
        _vars_['security-db'] = Path(srv.info.security_database)
        _vars_['arch'] = srv.info.architecture
        #if _vars_['bin-dir'] is None:
            #path = _vars_['home-dir'] / 'bin'
            #if path.is_dir():
                #_vars_['bin-dir'] = path
            #else:
                #pytest.exit("Path to binary tools not determined")
        #else:
            #_vars_['bin-dir'] = Path(_vars_['bin-dir'])
    # tools
    for tool in ['isql', 'gbak', 'nbackup', 'gstat', 'gfix', 'gsec']:
        set_tool(tool)


def pytest_collection_modifyitems(session, config, items):
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    skip_platform = pytest.mark.skip(reason=f"test not designed for {_platform}")
    # Apply skip markers
    for item in items:
        if 'slow' in item.keywords and not _vars_['runslow']:
            item.add_marker(skip_slow)
    # Deselect tests not applicable to tested engine version and platform
    selected = []
    deselected = []
    for item in items:
        platform_ok = True
        for platforms in [mark.args for mark in item.iter_markers(name="platform")]:
            platform_ok = _platform in platforms
        versions = [mark.args for mark in item.iter_markers(name="version")]
        if versions:
            spec = SpecifierSet(','.join(list(versions[0])))
            if platform_ok and _vars_['version'] in spec:
                selected.append(item)
            else:
                deselected.append(item)
    items[:] = selected
    config.hook.pytest_deselected(items=deselected)

@pytest.fixture(autouse=True)
def firebird_server():
    with connect_server(_vars_['server']) as srv:
        yield srv

def substitute_macros(text: str, macros: Dict[str, str]):
    f_text = text
    for (pattern, replacement) in macros.items():
        replacement = replacement.replace(os.path.sep,'/')
        f_text = f_text.replace(f'$({pattern.upper()})', replacement)
    return f_text

class Database:
    ""
    def __init__(self, path: Path, filename: str='test.fdb',
                 user: str=None, password: str=None):
        self.db_path: Path = path / filename
        self.dsn: str = None
        self.io_enc = 'utf8'
        if _vars_['host']:
            self.dsn = f"{_vars_['host']}:{str(self.db_path)}"
        else:
            self.dsn = str(self.db_path)
        self.subs = {'temp_directory': str(path / 'x')[:-1],
                     'database_location': str(path / 'x')[:-1],
                     'DATABASE_PATH': str(path / 'x')[:-1],
                     'DSN': self.dsn,
                     'files_location': str(_vars_['root'] / 'files'),
                     'backup_location': str(_vars_['root'] / 'backups'),
                     'suite_database_location': str(_vars_['root'] / 'databases'),
                     }
        srv_conf = driver_config.get_server(_vars_['server'])
        self.user: str = srv_conf.user.value if user is None else user
        self.password: str = srv_conf.password.value if password is None else password
    def _make_config(self, page_size: int=None, sql_dialect: int=None, charset: str=None) -> None:
        db_conf = driver_config.get_database('pytest')
        db_conf.clear()
        db_conf.server.value = _vars_['server']
        db_conf.database.value = str(self.db_path)
        db_conf.user.value = self.user
        db_conf.password.value = self.password
        if sql_dialect is not None:
            db_conf.db_sql_dialect.value = sql_dialect
        if page_size is not None:
            db_conf.page_size.value = page_size
        if charset is not None:
            db_conf.db_charset.value = charset
        if _vars_['protocol'] is not None:
            db_conf.protocol.value = NetProtocol._member_map_[_vars_['protocol'].upper()]
    def create(self, page_size: int=None, sql_dialect: int=None, charset: str=None) -> None:
        #__tracebackhide__ = True
        self._make_config(page_size, sql_dialect, charset)
        print(f"Creating db: {self.db_path} [{page_size=}, {sql_dialect=}, {charset=}, user={self.user}, password={self.password}]")
        db = create_database('pytest')
        db.close()
    def restore(self, backup: str) -> None:
        #__tracebackhide__ = True
        fbk_file: Path = _vars_['backups'] / backup
        if not fbk_file.is_file():
            raise ValueError(f"Backup file '{fbk_file}' not found")
        print(f"Restoring db: {self.db_path} from {fbk_file}")
        result = run([_vars_['gbak'], '-r', '-v', '-user', self.user,
                      '-password', self.password,
                      str(fbk_file), str(self.dsn)], capture_output=True)
        if result.returncode:
            print(f"-- stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("Database restore failed")
        # Fix permissions
        #if platform.system != 'Windows':
            #os.chmod(self.db_path, 16895)
        return result
    def copy(self, filename: str) -> None:
        #__tracebackhide__ = True
        src_path = _vars_['databases'] / filename
        #print(f"Copying db: {self.db_path} from {src_path}")
        shutil.copyfile(src_path, self.db_path)
        # Fix permissions
        if platform.system != 'Windows':
            os.chmod(self.db_path, 16895)
    def init(self, script: str) -> CompletedProcess:
        #__tracebackhide__ = True
        #print("Running init script")
        result = run([_vars_['isql'], '-ch', 'utf8', '-user', self.user,
                      '-password', self.password, str(self.dsn)],
                     input=substitute_macros(script, self.subs),
                     encoding='utf8', capture_output=True)
        if result.returncode:
            print(f"-- stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("Database init script execution failed")
        return result
    def execute(self, script: str, *, raise_on_fail: bool, charset: str='utf8') -> CompletedProcess:
        __tracebackhide__ = True
        #print("Running test script")
        if charset:
            charset = charset.upper()
        else:
            charset = 'NONE'
        self.io_enc = CHARSET_MAP[charset]
        result = run([_vars_['isql'], '-ch', charset, '-user', self.user,
                      '-password', self.password, str(self.dsn)],
                     input=substitute_macros(script, self.subs),
                     encoding=self.io_enc, capture_output=True)
        if result.returncode and raise_on_fail:
            print(f"-- ISQL script stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- ISQL script stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("ISQL script execution failed")
        return result
    def drop(self) -> None:
        self._make_config()
        db = connect('pytest')
        #print(f"Removing db: {self.db_path}")
        db.drop_database()

@pytest.fixture
def db_path(tmp_path) -> Path:
    if platform.system != 'Windows':
        base = _vars_['basetemp']
        if base is None:
            os.chmod(tmp_path.parent, 16895)
            os.chmod(tmp_path.parent.parent, 16895)
        else:
            os.chmod(Path(base), 16895)
        os.chmod(tmp_path, 16895)
    return tmp_path

class User:
    def __init__(self, name: str, password: str, server: Server):
        self.name: str = name
        self.password: str = password
        self.server: Server = server
    def create(self) -> None:
        if self.server.user.exists(self.name):
            self.drop()
        self.server.user.add(user_name=self.name, password=self.password)
        #print(f"User {self.name} created")
    def drop(self) -> None:
        self.server.user.delete(self.name)
        #print(f"User {self.name} dropped")

def user_factory(*, name: str, password: str) -> None:

    @pytest.fixture
    def user_fixture(request: FixtureRequest, firebird_server) -> User:
        user = User(name, password, firebird_server)
        user.create()
        yield user
        user.drop()

    return user_fixture

def db_factory(*, filename: str='test.fdb', init: str=None, from_backup: str=None,
               copy_of: str=None, page_size: int=None, sql_dialect: int=None,
               charset: str=None, user: str=None, password: str=None):

    @pytest.fixture
    def database_fixture(request: FixtureRequest, db_path) -> Database:
        db = Database(db_path, filename, user, password)
        if from_backup is None and copy_of is None:
            db.create(page_size, sql_dialect, charset)
        elif from_backup is not None:
            db.restore(from_backup)
        elif copy_of is not None:
            db.copy(copy_of)
        if init is not None:
            db.init(init)
        yield db
        db.drop()

    return database_fixture

class Action:
    def __init__(self, db: Database, script: str, substitutions: List[str], outfile: Path,
                 charset: str):
        self.db: Database = db
        self.script: str = script
        self.charset: str = charset
        self.return_code: int = 0
        self.stdout: str = ''
        self._clean_stdout: str = None
        self.stderr: str = ''
        self._clean_stderr: str = None
        self.expected_stdout: str = ''
        self._clean_expected_stdout: str = None
        self.expected_stderr: str = ''
        self._clean_expected_stderr: str = None
        self.substitutions: List[str] = [x for x in substitutions]
        self.outfile: Path = outfile
    def make_diff(self, left: str, right: str) -> str:
        return '\n'.join(difflib.ndiff(left.splitlines(), right.splitlines()))
    def space_strip(self, value: str) -> str:
        """Reduce spaces in value"""
        value= re.sub("(?m)^\\s+", "", value)
        return re.sub("(?m)\\s+$", "", value)
    def string_strip(self, value: str, substitutions: List[str]=[], isql: bool=True,
                     remove_space: bool=True) -> str:
        """Remove unwanted isql noise strings and apply substitutions defined
        in recipe to captured output value.
        """
        if not value:
            return value
        if isql:
            for regex in map(re.compile,['(?m)Database:.*\\n?', 'SQL>[ \\t]*\\n?',
                                       'CON>[ \\t]*\\n?', '-->[ \\t]*\\n?']):
                value = re.sub(regex, "", value)
        for pattern, replacement in substitutions:
            value= re.compile(pattern, re.M).sub(replacement, value)
        if remove_space:
            value = self.space_strip(value)
        return value
    def execute(self) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        result: CompletedProcess = self.db.execute(self.script,
                                                   raise_on_fail=not bool(self.expected_stderr),
                                                   charset=self.charset)
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=self.db.io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=self.db.io_enc)
    @property
    def clean_stdout(self) -> str:
        if self._clean_stdout is None:
            self._clean_stdout = self.string_strip(self.stdout, self.substitutions)
        return self._clean_stdout
    @property
    def clean_stderr(self) -> str:
        if self._clean_stderr is None:
            self._clean_stderr = self.string_strip(self.stderr, self.substitutions)
        return self._clean_stderr
    @property
    def clean_expected_stdout(self) -> str:
        if self._clean_expected_stdout is None:
            self._clean_expected_stdout = self.string_strip(self.expected_stdout, self.substitutions)
        return self._clean_expected_stdout
    @property
    def clean_expected_stderr(self) -> str:
        if self._clean_expected_stderr is None:
            self._clean_expected_stderr = self.string_strip(self.expected_stderr, self.substitutions)
        return self._clean_expected_stderr

def isql_act(db_fixture_name: str, script: str, *, substitutions: List[str]=None,
             charset: str='utf8'):

    @pytest.fixture
    def isql_act_fixture(request: FixtureRequest) -> Action:
        db: Database = request.getfixturevalue(db_fixture_name)
        f: Path = Path.cwd() / 'out' / request.module.__name__.replace('.', '/')
        if _vars_['save-output'] and not f.parent.exists():
            f.parent.mkdir(parents=True)
        f = f.with_name(f'{f.stem}-{request.function.__name__}.out')
        #f.write_text('stdout')
        result: Action = Action(db, script, substitutions, f, charset)
        return result

    return isql_act_fixture
