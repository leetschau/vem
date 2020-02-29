import sys
import shutil
import fire
import yaml
from pathlib import Path

NEW_PROF = Path('/tmp/init.vim')
BACKUP = Path('backup.vim')
TARGET_NAME = Path('init.vim')
BASE_CONFIG = Path('base.yml')
TEXT_CONFIG = Path('text.yml')

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
        return config

    def applyProfile(self, profile:str):
        with open(NEW_PROF, 'w') as f:
            f.write(profile)
        print('  New profile generated at %s' % NEW_PROF)

        shutil.copy2(self._prof_target / TARGET_NAME, self._prof_base / BACKUP)
        print('  Backup original profile to %s' % self._prof_base / BACKUP)

        self._prof_target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(NEW_PROF, self._prof_target)
        print('  Copy generated file from %s to %s' % (NEW_PROF, self._prof_target))

    def set_base(self):
        print('Set vim profile to base level ...')
        config = self.load_config(BASE_CONFIG)['conf']
        self.applyProfile(config)

    def set_text(self):
        print('Set vim profile to text level ...')
        
    def set_lang(self, langs):
        lang_names = langs.split('-')
        print('Set vim profile to IDE level with language plugins:')
        print(lang_names)


class App:
    """vim environment manager

    Setup vim configuration files as you wish.
    Override default settings with --prof-base or/and --prof-target
    Paths are all relative to $HOME folder.
    E.g.: vem --prof-base=".vim" ...
    """
    def __init__(self, prof_base='Documents/sources/vem/profiles',
                 prof_target='Documents/sources/.config/nvim'):
        self._prof_base = Path.home() / Path(prof_base)
        self._prof_target = Path.home() / Path(prof_target)
        self._profileSetter = ProfileSetter(self._prof_base,
                self._prof_target)
        print('Profile base: %s' % self._prof_base)
        print('Profile target: %s' % self._prof_target)

    def st(self, level, langs=None):
        """set profile

        Set vim profile with specific level.
        level: base | text | langs
        langs: language list, seperated with hyphen
          E.g.: vem set langs python-nim-haskell
        """
        if level is 'base':
            self._profileSetter.set_base()
        elif level is 'text':
            self._profileSetter.set_text()
        elif level is 'langs':
            if langs is None:
                print('Languages not set!')
                print('Run `vem set -h` for details.')
            else:
                self._profileSetter.set_lang(langs)
        else:
            print('Invalid level name.\nRun `vem set -h` for help')

    def rb(self):
        """rollback profile

        Rollback to last vim profile.
        """
        print('Rollback to last profile ...')

    def up(self):
        """update profile

        Update vim profile with local configs.
        The level keep the same with the last settings.
        """
        print('Updating vim profile ...')


if __name__ == '__main__':
    fire.Fire(App)
