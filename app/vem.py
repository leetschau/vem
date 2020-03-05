import sys
import shutil
import fire
import yaml
from pathlib import Path
from typing import List
from functools import reduce

NEW_PROF = Path('/tmp/init.vim')
BACKUP = Path('backup.vim')
BASE_CONFIG = Path('base.yml')
TEXT_CONFIG = Path('text.yml')
TARGET_FILE = {'neovim': Path.home() / Path('.config/nvim/init.vim'),
               'vim': Path.home() / Path('.vimrc')}
LANG_SEP = '+'


class ProfileSetter:
    def __init__(self, prof_base, prof_target):
        self._prof_base = prof_base
        self._prof_target = prof_target

    def load_config(self, config_file: Path) -> dict:
        fullpath = self._prof_base / config_file
        with open(fullpath, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                sys.stderr.write(f"YAML parse failed for file {fullpath}")
                sys.exit(1)
        return config

    def format_vam_plugins(self, plugins: List[dict]) -> str:
        # TODO: add support for other types
        return "VAMActivate " + ' '.join([
            f"github:{plugin.get('name')}" for plugin in plugins
            if plugin.get('type') == 'github']) + '\n\n'

    def apply_profile(self, profile: str):
        if not profile.startswith('"#'):
            sys.stderr.write(profile)
            sys.exit(2)

        with open(NEW_PROF, 'w') as f:
            f.write(profile)
        print('  New profile generated at %s' % NEW_PROF)

        if self._prof_target.exists():
            shutil.copy2(self._prof_target, self._prof_base / BACKUP)
            print('  Backup original profile to %s' % self._prof_base / BACKUP)
        else:
            print('  Origin profile not exists, skip backup')

        self._prof_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(NEW_PROF, self._prof_target)
        print(f'  Copy generated file from {NEW_PROF} to {self._prof_target}')

    def lang_config(self, base: str, lang: str) -> str:
        if not (self._prof_base / Path(lang + '.yml')).exists():
            return base
        config = self.load_config(self._prof_base / Path(lang + '.yml'))
        return base + f'\n" --- {lang} section ---\n' +\
            config.get('conf', '') +\
            '\n' + self.format_vam_plugins(config.get('plugins', ''))

    def set_profile(self, level: str, langs: str):
        configs = {}
        header = f'"# Created by vem\n"# Level: {level}, Langs: {langs}\n'
        configs['base'] = header +\
            self.load_config(BASE_CONFIG).get('conf', '')
        text_prof = self.load_config(TEXT_CONFIG)
        configs['text'] = configs.get('base') +\
            '\n\n\n" --- text section ---\n\n' +\
            text_prof.get('conf', '') + '\n' +\
            self.format_vam_plugins(text_prof.get('plugins', ''))
        configs['langs'] = configs.get('text') +\
            reduce(self.lang_config,
                   [] if langs is None else langs.split(LANG_SEP), "")
        self.apply_profile(
            configs.get(level,
                        'Invalid level name.\nRun `vem st -h` for help\n'))

    def rollback_profile(self):
        fullpath = self._prof_base / BACKUP
        if fullpath.exists():
            with open(fullpath, 'r') as f:
                self.apply_profile(f.read())
        else:
            print("Backup file does not exist. Rollback cancelled.")

    def update_profile(self):
        if not self._prof_target.exists():
            errmsg = (f'File {self._prof_target} not exists in'
                      f'{self._prof_target}\n'
                      f'Use `st` command to generate one')
            sys.exit(errmsg)
        with open(self._prof_target, 'r') as f:
            secondLine = f.readlines()[1]
        if not secondLine.startswith('"#'):
            errmsg = 'Bad format to fetch previous level and langs params'
            sys.exit(errmsg)
        level = secondLine.split(', ')[0].split(': ')[1]
        langs_str = secondLine.split(', ')[1].split(': ')[1]
        langs = None if langs_str == 'None' else langs_str
        print(f"Update profile with level: {level} and langs: {langs}")
        self.set_profile(level, langs)


class App:
    """vim environment manager

    Setup vim configuration files as you wish.

    Override default settings with --prof-base or/and --mode

      --mode: create vim / neovim configuration file. Default: neovim

      --prof-base: the folder saving vem profiles, relative to $HOME folder.
        Default: .local/vem/profiles

    E.g.: vem st text
          vem st langs python
          vem st base --mode=vim
          vem st langs python+nim --prof-base=Documents/vem/profiles
    """
    def __init__(self, mode='neovim',
                 prof_base='.local/vem/profiles'):
        self._prof_base = Path.home() / Path(prof_base)
        self._prof_target = TARGET_FILE.get(mode if mode in TARGET_FILE
                                            else 'neovim')
        self._profileSetter = ProfileSetter(self._prof_base, self._prof_target)
        print('Profile base: %s' % self._prof_base)
        print('Profile target: %s' % self._prof_target)

    def st(self, level, langs=None):
        """set profile

        Set vim profile with specific level.
        level: base | text | langs
        langs: language list, seperated with hyphen
          E.g.: vem st langs python-nim-haskell
        """
        self._profileSetter.set_profile(level, langs)

    def rb(self):
        """rollback profile

        Rollback to last vim profile.
        """
        self._profileSetter.rollback_profile()

    def up(self):
        """update profile

        Update vim profile with local configs.
        The level keep the same with the last settings.
        """
        self._profileSetter.update_profile()


if __name__ == '__main__':
    fire.Fire(App)
