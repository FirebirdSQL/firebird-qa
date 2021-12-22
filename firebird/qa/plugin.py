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
from typing import List, Dict, Union, Optional
import os
import re
import shutil
import platform
import difflib
import pytest
from _pytest.fixtures import FixtureRequest
from subprocess import run, CompletedProcess, PIPE, STDOUT
from pathlib import Path
from configparser import ConfigParser, ExtendedInterpolation
from packaging.specifiers import SpecifierSet
from packaging.version import parse
import time
from threading import Thread, Barrier
from firebird.driver import connect, connect_server, create_database, driver_config, \
     NetProtocol, Server, CHARSET_MAP, Connection, Cursor, \
     DESCRIPTION_NAME, DESCRIPTION_DISPLAY_SIZE, DatabaseConfig, DBKeyScope, DbInfoCode, \
     DbWriteMode, get_api
from firebird.driver.core import _connect_helper

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
            f"  files: {_vars_['files']}",
            f"  driver configuration: {_vars_['firebird-config']}",
            f"  server: {_vars_['server']}",
            f"  protocol: {_vars_['protocol']}",
            f"  engine: v{_vars_['version']}, {_vars_['arch']}",
            f"  home: {_vars_['home-dir']}",
            f"  bin: {_vars_['bin-dir']}",
            f"  security db: {_vars_['security-db']}",
            f"  client library: {_vars_['fbclient']}",
            f"  run slow tests: {_vars_['runslow']}",
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
    path = config.rootpath / 'files'
    _vars_['files'] = path if path.is_dir() else config.rootpath
    _vars_['server'] = config.getoption('server')
    _vars_['protocol'] = config.getoption('protocol')
    _vars_['save-output'] = config.getoption('save_output')
    srv_conf = driver_config.get_server(_vars_['server'])
    _vars_['host'] = srv_conf.host.value if srv_conf is not None else ''
    _vars_['port'] = srv_conf.port.value if srv_conf is not None else ''
    _vars_['password'] = srv_conf.password.value
    #
    driver_config.register_database('employee')
    db_conf = driver_config.get_database('employee')
    db_conf.server.value = _vars_['server']
    db_conf.database.value = 'employee.fdb'
    # Handle server-specific "fb_client_library" configuration option
    _vars_['fbclient'] = 'UNKNOWN'
    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    cfg.read(str(config_path))
    if cfg.has_option(_vars_['server'], 'fb_client_library'):
        fbclient = Path(cfg.get(_vars_['server'], 'fb_client_library'))
        if not fbclient.is_file():
            pytest.exit(f"Client library '{fbclient}' not found!")
        driver_config.fb_client_library.value = str(fbclient)
    cfg.clear()
    # THIS should load the driver API, do not connect db or server earlier!
    _vars_['fbclient'] = get_api().client_library_name
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
    # tools
    for tool in ['isql', 'gbak', 'nbackup', 'gstat', 'gfix', 'gsec', 'fbsvcmgr']:
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

#@pytest.hookimpl(hookwrapper=True)
#def pytest_runtest_makereport(item, call):
    #outcome = yield
    #report = outcome.get_result()

    #test_fn = item.obj
    #docstring = getattr(test_fn, '__doc__')
    #if docstring:
        #report.nodeid = docstring

def substitute_macros(text: str, macros: Dict[str, str]):
    f_text = text
    for (pattern, replacement) in macros.items():
        replacement = replacement.replace(os.path.sep,'/')
        f_text = f_text.replace(f'$({pattern.upper()})', replacement)
    return f_text

class Database:
    ""
    def __init__(self, path: Path, filename: str='test.fdb',
                 user: str=None, password: str=None, charset: str=None, debug: str=''):
        self._debug: str = debug
        self.db_path: Path = path / filename
        self.dsn: str = None
        self.charset: str = 'NONE' if charset is None else charset.upper()
        self.io_enc: str = CHARSET_MAP[self.charset]
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
    def _make_config(self, *, page_size: int=None, sql_dialect: int=None, charset: str=None,
                     user: str=None, password: str=None) -> None:
        db_conf = driver_config.get_database('pytest')
        db_conf.clear()
        db_conf.server.value = _vars_['server']
        db_conf.database.value = str(self.db_path)
        db_conf.user.value = self.user if user is None else user
        db_conf.password.value = self.password if password is None else password
        if sql_dialect is not None:
            db_conf.db_sql_dialect.value = sql_dialect
            db_conf.sql_dialect.value = sql_dialect
        if page_size is not None:
            db_conf.page_size.value = page_size
        if charset is not None:
            db_conf.db_charset.value = charset
            db_conf.charset.value = charset
        if _vars_['protocol'] is not None:
            db_conf.protocol.value = NetProtocol._member_map_[_vars_['protocol'].upper()]
    def get_config(self) -> DatabaseConfig:
        return driver_config.get_database('pytest')
    def create(self, page_size: int=None, sql_dialect: int=None) -> None:
        #__tracebackhide__ = True
        self._make_config(page_size=page_size, sql_dialect=sql_dialect, charset=self.charset)
        charset = self.charset
        print(f"Creating db: {self.dsn} [{page_size=}, {sql_dialect=}, {charset=}, user={self.user}, password={self.password}]")
        with create_database('pytest'):
            pass
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
        result = run([_vars_['isql'], '-ch', 'UTF8', '-user', self.user,
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
    def drop(self) -> None:
        with connect_server(_vars_['server']) as srv:
            srv.database.no_linger(database=self.db_path)
        self._make_config()
        with connect('pytest') as db:
            db._att._name = self._debug
            try:
                db.execute_immediate('delete from mon$attachments where mon$attachment_id != current_connection')
                db.commit()
            except:
                pass
            #print(f"Removing db: {self.db_path}")
            try:
                db.drop_database()
            except:
                pass
        if self.db_path.is_file():
            self.db_path.unlink(missing_ok=True)
    def connect(self, *, user: str=None, password: str=None, role: str=None, no_gc: bool=None,
                no_db_triggers: bool=None, dbkey_scope: DBKeyScope=None,
                session_time_zone: str=None, charset: str=None, sql_dialect: int=None,
                auth_plugin_list: str=None) -> Connection:
        self._make_config(user=user, password=password, charset=charset, sql_dialect=sql_dialect)
        result = connect('pytest', role=role, no_gc=no_gc, no_db_triggers=no_db_triggers,
                       dbkey_scope=dbkey_scope, session_time_zone=session_time_zone,
                       auth_plugin_list=auth_plugin_list)
        result._att._name = self._debug
        return result
    def set_async_write(self) -> None:
        with connect_server(_vars_['server']) as srv:
            srv.database.set_write_mode(database=self.db_path, mode=DbWriteMode.ASYNC)
    def set_sync_write(self) -> None:
        with connect_server(_vars_['server']) as srv:
            srv.database.set_write_mode(database=self.db_path, mode=DbWriteMode.SYNC)

def db_factory(*, filename: str='test.fdb', init: str=None, from_backup: str=None,
               copy_of: str=None, page_size: int=None, sql_dialect: int=None,
               charset: str=None, user: str=None, password: str=None,
               do_not_create: bool=False, do_not_drop: bool=False, async_write: bool=True):

    @pytest.fixture
    def database_fixture(request: FixtureRequest, db_path) -> Database:
        db = Database(db_path, filename, user, password, charset, debug=str(request.module))
        if not do_not_create:
            if from_backup is None and copy_of is None:
                db.create(page_size, sql_dialect)
            elif from_backup is not None:
                db.restore(from_backup)
            elif copy_of is not None:
                db.copy(copy_of)
            if async_write:
                db.set_async_write()
            if init: # Do not check for None, we want to skip empty scripts as well
                db.init(init)
        yield db
        if not do_not_drop:
            db.drop()

    return database_fixture

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
    def __init__(self, db: Database, *, name: str, password: str, plugin: str, charset: str,
                 active: bool=True, tags: Dict[str]=None, first_name: str=None,
                 middle_name: str=None, last_name: str=None, admin: bool=False,
                 do_not_create: bool=False):
        self.db: Database = db
        self.__name: str = name if name.startswith('"') else name.upper()
        self.__password: str = password
        self.__plugin: str = plugin
        self.__p = ''  if self.__plugin is None else f" USING PLUGIN {self.__plugin}"
        self.charset: str = charset
        self.__active: bool = active
        self.__first_name: str = first_name
        self.__middle_name: str = middle_name
        self.__last_name: str = last_name
        self.__tags: Dict[str] = tags
        self.__admin: bool = admin
        self.__create: bool = not do_not_create
    def __enter__(self) -> Role:
        if self.__create and not self.exists():
            self.create()
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.exists():
            self.drop()
    def exists(self) -> bool:
        with self.db.connect(charset=self.charset) as con:
            c = con.cursor()
            name = self.name[1:-1] if self.name.startswith('"') else self.name
            cmd = f"SELECT COUNT(*) FROM SEC$USERS WHERE SEC$USER_NAME = '{name}'"
            if self.__plugin is not None:
                cmd += f" AND SEC$PLUGIN = '{self.__plugin}'"
            cnt = c.execute(cmd).fetchone()[0]
        return cnt > 0
    def create(self) -> None:
        if self.exists():
            self.drop()
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f"CREATE USER {self.name} PASSWORD '{self.__password}' {'ACTIVE' if self.__active else 'INACTIVE'}{self.__p}{' GRANT ADMIN ROLE' if self.__admin else ''}")
            if self.__first_name is not None:
                con.execute_immediate(f"ALTER USER {self.name} SET FIRSTNAME '{self.__first_name}'{self.__p}")
            if self.__middle_name is not None:
                con.execute_immediate(f"ALTER USER {self.name} SET MIDDLENAME '{self.__middle_name}'{self.__p}")
            if self.__last_name is not None:
                con.execute_immediate(f"ALTER USER {self.name} SET LASTNAME '{self.__last_name}'{self.__p}")
            if self.__tags is not None:
                tags = ', '.join([f"{name} = '{value}'" for name, value in self.__tags.items()])
                con.execute_immediate(f"ALTER USER {self.name} SET TAGS ({tags}){self.__p}")
            con.commit()
        print(f"CREATE user: {self.name} PLUGIN: {self.plugin}")
    def drop(self) -> None:
        with self.db.connect(charset=self.charset) as con:
            c = con.cursor()
            grants = c.execute('select count(*) from '\
                               '(select rdb$user as a from rdb$user_privileges '\
                               'union all select sec$user as a from sec$db_creators) '\
                               'where a = ?',
                               [self.name if self.name.startswith('"') else self.name.upper()]).fetchone()[0]
            if grants > 0:
                c.execute(f'revoke all on all from {self.name}')
                con.commit()
            #
            print(f"DROP user: {self.name} PLUGIN: {self.plugin}")
            con.execute_immediate(f"DROP USER {self.name}{self.__p}")
            con.commit()
    def set_tag(self, name: str, *, value: str) -> None:
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f"ALTER USER {self.name} TAGS ({name} = '{value}'){self.__p}")
            con.commit()
    def drop_tag(self, name: str) -> None:
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f"ALTER USER {self.name} TAGS (DROP {name}){self.__p}")
            con.commit()
    @property
    def name(self) -> str:
        return self.__name
    @property
    def plugin(self) -> str:
        if self.__plugin is None:
            with self.db.connect() as con:
                c = con.cursor()
                self.__plugin = c.execute(f'SELECT SEC$PLUGIN FROM SEC$USERS').fetchone()[0].strip()
        return self.__plugin
    @property
    def password(self) -> str:
        return self.__password
    @password.setter
    def password(self, value: str) -> None:
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f"ALTER USER {self.__name} SET PASSWORD '{value}'")
            con.commit()
        self.__password = value
    @property
    def first_name(self) -> str:
        return self.__first_name
    @first_name.setter
    def first_name(self, value: str) -> None:
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f"ALTER USER {self.__name} SET FIRSTNAME '{value}'")
            con.commit()
        self.__first_name = value
    @property
    def middle_name(self) -> str:
        return self.__middle_name
    @middle_name.setter
    def middle_name(self, value: str) -> None:
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f"ALTER USER {self.__name} SET MIDDLENAME '{value}'")
            con.commit()
        self.__middle_name = value
    @property
    def last_name(self) -> str:
        return self.__last_name
    @last_name.setter
    def last_name(self, value: str) -> None:
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f"ALTER USER {self.__name} SET LASTNAME '{value}'")
            con.commit()
        self.__last_name = value
    @property
    def tags(self) -> Dict[str]:
        return dict(self.__tags)

def user_factory(db_fixture_name: str, *, name: str, password: str, plugin: str=None,
                 charset: str='utf8', active: bool=True, tags: Dict[str]=None,
                 first_name: str=None, middle_name: str=None, last_name: str=None,
                 admin: bool=False, do_not_create: bool=False):

    @pytest.fixture
    def user_fixture(request: FixtureRequest) -> User:
        with User(request.getfixturevalue(db_fixture_name), name=name, password=password,
                  plugin=plugin, charset=charset, active=active, tags=tags,
                  first_name=first_name, middle_name=middle_name, last_name=last_name,
                  admin=admin, do_not_create=do_not_create) as user:
            yield user

    return user_fixture

def trace_thread(act: Action, b: Barrier, cfg: List[str], output: List[str], keep_log: bool, encoding: str):
    with act.connect_server() as srv:
        srv.encoding = encoding
        srv.trace.start(config='\n'.join(cfg))
        b.wait()
        for line in srv:
            if keep_log:
                output.append(line)

class TraceSession:
    def __init__(self, act: Action, config: List[str], keep_log: bool=True, encoding: str='ascii'):
        self.act: Action = act
        self.config: List[str] = config
        self.output: List[str] = []
        self.keep_log: bool = keep_log
        self.trace_thread: Thread = None
        self.encoding: str = encoding
    def __enter__(self) -> TraceSession:
        b = Barrier(2)
        self.trace_thread = Thread(target=trace_thread, args=[self.act, b, self.config,
                                                              self.output, self.keep_log,
                                                              self.encoding])
        self.trace_thread.start()
        b.wait()
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        time.sleep(2)
        with self.act.connect_server() as srv:
            for session in list(srv.trace.sessions.keys()):
                srv.trace.stop(session_id=session)
            self.trace_thread.join(5.0)
            if self.trace_thread.is_alive():
                pytest.fail('Trace thread still alive')
        self.act.trace_log = self.output

class ServerKeeper:
    def __init__(self, act: Action, server: str):
        self.act: Action = act
        self.server:str = server
        self.old_value = None
    def __enter__(self):
        self.old_value = self.act.vars['server']
        self.act.vars['server'] = self.server
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.old_value is not None:
            self.act.vars['server'] = self.old_value

class Envar:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value
        self.old_value = None
    def __enter__(self) -> Envar:
        if self.name in os.environ:
            self.old_value = os.environ[self.name]
        os.environ[self.name] = self.value
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.old_value is not None:
            os.environ[self.name] = self.old_value

def envar_factory(*, name: str, value: str):

    @pytest.fixture
    def envar_fixture() -> User:
        with Envar(name, value) as envar:
            yield envar

    return envar_fixture

class Role:
    def __init__(self, database: Database, name: str, charset: str, do_not_create: bool):
        self.db: Database = database
        self.name: str = name if name.startswith('"') else name.upper()
        self.charset = charset
        self.do_not_create: bool = do_not_create
    def __enter__(self) -> Role:
        if not self.exists() and not self.do_not_create:
            self.create()
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.exists():
            self.drop()
    def create(self) -> None:
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f'CREATE ROLE {self.name}')
            con.commit()
            print(f"CREATE role: {self.name}")
    def drop(self) -> None:
        with self.db.connect(charset=self.charset) as con:
            con.execute_immediate(f'DROP ROLE {self.name}')
            con.commit()
            print(f"DROP role: {self.name}")
    def exists(self) -> bool:
        with self.db.connect(charset=self.charset) as con:
            c = con.cursor()
            name = self.name[1:-1] if self.name.startswith('"') else self.name
            cmd = f"SELECT COUNT(*) FROM RDB$ROLES WHERE RDB$ROLE_NAME = '{name}'"
            cnt = c.execute(cmd).fetchone()[0]
        return cnt > 0

def role_factory(db_fixture_name: str, *, name: str, charset: str='utf8', do_not_create: bool=False):

    @pytest.fixture
    def role_fixture(request: FixtureRequest) -> User:
        with Role(request.getfixturevalue(db_fixture_name), name, charset, do_not_create) as role:
            yield role

    return role_fixture

class Action:
    def __init__(self, db: Database, script: str, substitutions: List[str], outfile: Path):
        self.db: Database = db
        self.script: str = script
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
        self.trace_log: List[str] = []
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
    def execute(self, *, do_not_connect: bool=False, charset: str=None,
                combine_output: bool=False) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        if charset is not None:
            charset = charset.upper()
            io_enc = CHARSET_MAP[charset]
        else:
            charset = self.db.charset
            io_enc = self.db.io_enc
        params = [_vars_['isql'], '-ch', charset]
        if not do_not_connect:
            params.extend(['-user', self.db.user, '-password', self.db.password, str(self.db.dsn)])
        if combine_output:
            result: CompletedProcess = run(params, input=substitute_macros(self.script, self.db.subs),
                                           encoding=io_enc, stdout=PIPE, stderr=STDOUT)
        else:
            result: CompletedProcess = run(params, input=substitute_macros(self.script, self.db.subs),
                                           encoding=io_enc, capture_output=True)
        if result.returncode and not bool(self.expected_stderr) and not combine_output:
            print(f"-- ISQL script stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- ISQL script stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("ISQL script execution failed")

        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding='utf8')
            if self.stderr:
                err_file.write_text(self.stderr, encoding='utf8')
    def extract_meta(self, *, from_db: Database=None, charset: str=None,
                     io_enc: str=None) -> str:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        db = self.db if from_db is None else from_db
        charset = charset.upper() if charset else self.db.charset
        if io_enc is None:
            io_enc = CHARSET_MAP[charset]
        result = run([_vars_['isql'], '-x', '-ch', charset, '-user', db.user,
                      '-password', db.password, str(db.dsn)],
                     encoding=io_enc, capture_output=True)
        if result.returncode:
            print(f"-- ISQL stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- ISQL stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("ISQL execution failed")
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=self.db.io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=self.db.io_enc)
        return self.stdout
    def gstat(self, *, switches: List[str], charset: str=None, connect_db: bool=True,
              credentials: bool=True) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        #
        charset = charset.upper() if charset else self.db.charset
        io_enc = CHARSET_MAP[charset]
        params = [_vars_['gstat']]
        if credentials:
            params.extend(['-user', self.db.user, '-password', self.db.password])
        params.extend(switches)
        if connect_db:
            params.append(str(self.db.dsn))
        result: CompletedProcess = run(params,
                                       encoding=io_enc, capture_output=True)
        if result.returncode and not bool(self.expected_stderr):
            print(f"-- gstat stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- gstat stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("gstat execution failed")
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=self.db.io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=self.db.io_enc)
    def gsec(self, *, switches: List[str]=None, charset: str=None, io_enc: str=None,
             input: str=None, credentials: bool=True) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        #
        charset = charset.upper() if charset else self.db.charset
        if io_enc is None:
            io_enc = CHARSET_MAP[charset]
        params = [_vars_['gsec']]
        if switches:
            params.extend(switches)
        if credentials:
            params.extend(['-user', self.db.user, '-password', self.db.password])
        result: CompletedProcess = run(params, input=input,
                                       encoding=io_enc, capture_output=True)
        if result.returncode and not bool(self.expected_stderr):
            print(f"-- gsec stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- gsec stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("gsec execution failed")
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=io_enc)
    def gbak(self, *, switches: List[str]=None, charset: str=None, io_enc: str=None,
             input: str=None, credentials: bool=True, combine_output: bool=False) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        #
        charset = charset.upper() if charset else self.db.charset
        if io_enc is None:
            io_enc = CHARSET_MAP[charset]
        params = [_vars_['gbak']]
        if credentials:
            params.extend(['-user', self.db.user, '-password', self.db.password])
        if switches:
            params.extend(switches)
        if combine_output:
            result: CompletedProcess = run(params, input=input,
                                           encoding=io_enc, stdout=PIPE, stderr=STDOUT)
        else:
            result: CompletedProcess = run(params, input=input,
                                           encoding=io_enc, capture_output=True)
        if result.returncode and not (bool(self.expected_stderr) or combine_output):
            print(f"-- gbak stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- gbak stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("gbak execution failed")
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=io_enc)
    def nbackup(self, *, switches: List[str], charset: str=None, credentials: bool=True,
                combine_output: bool=False) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        #
        charset = charset.upper() if charset else self.db.charset
        io_enc = CHARSET_MAP[charset]
        params = [_vars_['nbackup']]
        params.extend(switches)
        if credentials:
            params.extend(['-user', self.db.user, '-password', self.db.password])
        if combine_output:
            result: CompletedProcess = run(params, encoding=io_enc, stdout=PIPE, stderr=STDOUT)
        else:
            result: CompletedProcess = run(params, encoding=io_enc, capture_output=True)
        if result.returncode and not (bool(self.expected_stderr) or combine_output):
            print(f"-- nbackup stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- nbackup stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("nbackup execution failed")
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=self.db.io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=self.db.io_enc)
    def gfix(self, *, switches: List[str]=None, charset: str=None, io_enc: str=None,
             input: str=None, credentials: bool=True) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        #
        charset = charset.upper() if charset else self.db.charset
        if io_enc is None:
            io_enc = CHARSET_MAP[charset]
        params = [_vars_['gfix']]
        if switches:
            params.extend(switches)
        if credentials:
            params.extend(['-user', self.db.user, '-password', self.db.password])
        result: CompletedProcess = run(params, input=input,
                                       encoding=io_enc, capture_output=True)
        if result.returncode and not bool(self.expected_stderr):
            print(f"-- gfix stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- gfix stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("gfix execution failed")
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=io_enc)
    def isql(self, *, switches: List[str], charset: str=None, io_enc: str=None,
             input: str=None, input_file: Path=None, connect_db: bool=True,
             credentials: bool=True, combine_output: bool=False, use_db: Database=None) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        #
        db = self.db if use_db is None else use_db
        charset = charset.upper() if charset else db.charset
        params = [_vars_['isql'], '-ch', charset]
        if io_enc is None:
            io_enc = CHARSET_MAP[charset]
        if credentials:
            params.extend(['-user', db.user, '-password', db.password])
        params.extend(switches)
        if input_file is not None:
            params.extend(['-i', str(input_file)])
        if connect_db:
            params.append(str(db.dsn))
        if combine_output:
            result: CompletedProcess = run(params, input=input,
                                           encoding=io_enc, stdout=PIPE, stderr=STDOUT)
        else:
            result: CompletedProcess = run(params, input=input,
                                           encoding=io_enc, capture_output=True)
        if result.returncode and not (bool(self.expected_stderr) or combine_output):
            print(f"-- isql stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- isql stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("isql execution failed")
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=io_enc)
    def svcmgr(self, *, switches: List[str]=None, charset: str=None, io_enc: str=None,
               connect_mngr: bool=True) -> None:
        __tracebackhide__ = True
        out_file: Path = self.outfile.with_suffix('.out')
        err_file: Path = self.outfile.with_suffix('.err')
        if out_file.is_file():
            out_file.unlink()
        if err_file.is_file():
            err_file.unlink()
        #
        charset = charset.upper() if charset else self.db.charset
        if io_enc is None:
            io_enc = CHARSET_MAP[charset]
        params = [_vars_['fbsvcmgr']]
        if connect_mngr:
            params.extend([f"{_vars_['host']}:service_mgr" if _vars_['host'] else 'service_mgr',
                           'user', self.db.user, 'password', self.db.password])
        if switches:
            params.extend(switches)
        result: CompletedProcess = run(params, encoding=io_enc, capture_output=True)
        if result.returncode and not bool(self.expected_stderr):
            print(f"-- fbsvcmgr stdout {'-' * 20}")
            print(result.stdout)
            print(f"-- fbsvcmgr stderr {'-' * 20}")
            print(result.stderr)
            raise Exception("fbsvcmgr execution failed")
        self.return_code: int = result.returncode
        self.stdout: str = result.stdout
        self.stderr: str = result.stderr
        # Store output
        if _vars_['save-output']:
            if self.stdout:
                out_file.write_text(self.stdout, encoding=io_enc)
            if self.stderr:
                err_file.write_text(self.stderr, encoding=io_enc)
    def connect_server(self, *, user: str='SYSDBA', password: str=None, role: str=None) -> Server:
        return connect_server(_vars_['server'], user=user,
                              password=_vars_['password'] if password is None else password,
                              role=role)
    def get_firebird_log(self) -> List[str]:
        with self.connect_server() as srv:
            srv.info.get_log()
            return srv.readlines()
    def is_version(self, version_spec: str) -> bool:
        spec = SpecifierSet(version_spec)
        return _vars_['version'] in spec
    def get_server_architecture(self) -> str:
        with self.db.connect() as con1, self.db.connect() as con2:
            sql = f"""
            select count(distinct a.mon$server_pid), min(a.mon$remote_protocol),
            max(iif(a.mon$remote_protocol is null, 1, 0))
            from mon$attachments a
            where a.mon$attachment_id in ({con1.info.id}, {con2.info.id}) or upper(a.mon$user) = upper('cache writer')
        """
            cur1 = con1.cursor()
            cur1.execute(sql)
            server_cnt, server_pro, cache_wrtr = cur1.fetchone()
            if server_pro is None:
                result = 'Embedded'
            elif cache_wrtr == 1:
                result = 'SS'
            elif server_cnt == 2:
                result = 'CS'
            else:
                f1 = con1.info.get_info(DbInfoCode.FETCHES)
                cur2 = con2.cursor()
                cur2.execute('select 1 from rdb$database').fetchall()
                f2 = con1.info.get_info(DbInfoCode.FETCHES)
                result = 'SC' if f1 == f2 else 'SS'
        return result
    def get_dsn(self, filename: Union[str, Path], protocol: str=None) -> str:
        return _connect_helper('', self.host, self.port, str(filename),
                               protocol if protocol else self.protocol)
    def reset(self) -> None:
        self.return_code: int = 0
        self._clean_stdout = None
        self._clean_stderr = None
        self._clean_expected_stdout = None
        self._clean_expected_stderr = None
        #
        self.expected_stdout = ''
        self.expected_stderr = ''
        self.stdout = ''
        self.stderr = ''
    def print_data(self, cursor: Cursor) -> None:
        # Print a header.
        for fieldDesc in cursor.description:
            print (fieldDesc[DESCRIPTION_NAME].ljust(fieldDesc[DESCRIPTION_DISPLAY_SIZE]),end=' ')
        print('')
        for fieldDesc in cursor.description:
            print ("-" * max((len(fieldDesc[DESCRIPTION_NAME]),fieldDesc[DESCRIPTION_DISPLAY_SIZE])),end=' ')
        print('')
        # For each row, print the value of each field left-justified within
        # the maximum possible width of that field.
        fieldIndices = range(len(cursor.description))
        for row in cursor:
            for fieldIndex in fieldIndices:
                fieldValue = row[fieldIndex]
                if not isinstance(fieldValue, str):
                    fieldValue = str(fieldValue)
                fieldMaxWidth = max((len(cursor.description[fieldIndex][DESCRIPTION_NAME]),cursor.description[fieldIndex][DESCRIPTION_DISPLAY_SIZE]))
                print (fieldValue.ljust(fieldMaxWidth), end=' ')
            print('')
    def print_data_list(self, cursor: Cursor, *, prefix: str='') -> None:
        for row in cursor:
            i = 0
            for fieldDesc in cursor.description:
                print(f'{prefix}{fieldDesc[DESCRIPTION_NAME].ljust(32)}{row[i]}')
                i += 1
            print()
    def trace(self, *, db_events: List[str]=None, svc_events: List[str]=None,
              config: List[str]=None, keep_log: bool=True, encoding: str='ascii',
              database: str=None) -> TraceSession:
        if config is not None:
            return TraceSession(self, config, keep_log=keep_log, encoding=encoding)
        else:
            config = []
            if db_events:
                database = self.db.db_path.name if database is None else database
                config.extend([f'database=%[\\\\/]{database}', '{', 'enabled = true'])
                config.extend(db_events)
                config.append('}')
            if svc_events:
                config.extend(['services', '{', 'enabled = true'])
                config.extend(svc_events)
                config.append('}')
            return TraceSession(self, config, keep_log=keep_log, encoding=encoding)
    def trace_to_stdout(self, *, upper: bool=False) -> None:
        log = ''.join(self.trace_log)
        self.stdout = log.upper() if upper else log
    def envar(self, name: str, value: str) -> Envar:
        return Envar(name, value)
    def match_any(self, line: str, patterns) -> bool:
        for pattern in patterns:
            if pattern.search(line):
                return True
        return False
    def print_callback(self, line: str) -> None:
        print(line, end='')
    def get_config(self, key: str) -> Optional[str]:
        with connect('employee') as con:
            c = con.cursor()
            row = c.execute('select RDB$CONFIG_VALUE from rdb$config where upper(RDB$CONFIG_NAME) = ?', [key.upper()]).fetchone()
        return row[0] if row else None
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
    @property
    def vars(self) -> Dict[str]:
        return _vars_
    @property
    def host(self) -> str:
        return _vars_['host']
    @property
    def port(self) -> str:
        return _vars_['port']
    @property
    def protocol(self) -> str:
        return _vars_['protocol']
    @property
    def security_db(self) -> str:
        return _vars_['security-db']
    @property
    def home_dir(self) -> Path:
        return _vars_['home-dir']
    @property
    def bin_dir(self) -> Path:
        return _vars_['bin-dir']
    @property
    def platform(self) -> str:
        return _platform

def isql_act(db_fixture_name: str, script: str, *, substitutions: List[str]=None):

    @pytest.fixture
    def isql_act_fixture(request: FixtureRequest) -> Action:
        db: Database = request.getfixturevalue(db_fixture_name)
        f: Path = Path.cwd() / 'out' / request.module.__name__.replace('.', '/')
        if _vars_['save-output'] and not f.parent.exists():
            f.parent.mkdir(parents=True)
        f = f.with_name(f'{f.stem}-{request.function.__name__}.out')
        result: Action = Action(db, script, substitutions, f)
        return result

    return isql_act_fixture

def python_act(db_fixture_name: str, *, substitutions: List[str]=None):

    @pytest.fixture
    def python_act_fixture(request: FixtureRequest) -> Action:
        db: Database = request.getfixturevalue(db_fixture_name)
        f: Path = Path.cwd() / 'out' / request.module.__name__.replace('.', '/')
        if _vars_['save-output'] and not f.parent.exists():
            f.parent.mkdir(parents=True)
        f = f.with_name(f'{f.stem}-{request.function.__name__}.out')
        result: Action = Action(db, '', substitutions, f)
        return result

    return python_act_fixture

def temp_file(filename: str):

    @pytest.fixture
    def temp_file_fixture(tmp_path):
        tmp_file = tmp_path / filename
        yield tmp_file
        if tmp_file.is_file():
            tmp_file.unlink()

    return temp_file_fixture

def temp_files(filenames: List[str]):

    @pytest.fixture
    def temp_files_fixture(tmp_path):
        tmp_files = []
        for filename in filenames:
            tmp_files.append(tmp_path / filename)
        yield tmp_files
        for tmp_file in tmp_files:
            if tmp_file.is_file():
                tmp_file.unlink()

    return temp_files_fixture

