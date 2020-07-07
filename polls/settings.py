import pathlib

import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
config_dir = BASE_DIR / 'config'


def _get_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config


def get_real_config(*path):
    config = {}
    for config_file in path:
        config_path = config_dir / config_file
        config.update(_get_config(config_path))
    return config
