import os


def repo_root():
    return os.path.abspath(os.path.join(__file__, os.pardir))


def sprites_path():
    return os.path.join(repo_root(), 'res/sprites')


def music_levels_path(level_name):
    return os.path.join(repo_root(), f'res/music/levels/{level_name}.wav')


def sounds_path(sound_name):
    return os.path.join(repo_root(), f'res/music/sounds/{sound_name}.wav')


def background_path(bg_name):
    return os.path.join(repo_root(), f'res/backgrounds/{bg_name}')
