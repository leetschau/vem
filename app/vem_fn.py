import sys
import fire

profile_base = 
profile_target = 

def set_profile(level, lang=None):
    """set vim profile with specific level

    level: base | text | lang
    lang: language list, seperated with comma.
          E.g.: python,nim,haskell
    """
    if (level is 'lang') and (lang is None):
        print('lang param must be specified when level is lang')
        print('E.g.: vem set lang python,nim')
        sys.exit(1)
    print('Set vim profile to level: %s' % level)
    if level is 'base':
        set_base()
    elif level is 'text':
        set_text()
    elif level is 'lang':
        print('with language pack: %s' % lang)
        set_lang(lang)
    else:
        print('Invalid level name.\nRun `vem set -h` for help')

def rollback_profile():
    """rollback to last vim profile
    """
    print('Rollback to last profile ...')

def update_profile():
    """update vim profile with local configs
       with the same level of last setting
    """
    print('Updating vim profile ...')

if __name__ == '__main__':
    fire.Fire({
        'set': set_profile,
        'rb': rollback_profile,
        'up': update_profile,
    })
