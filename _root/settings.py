import pathlib

import yaml

my_path = pathlib.Path(__file__).parent
BASE_DIR = my_path.parent
config_dir = my_path / 'config'


def _get_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config


def get_real_config(*path):
    config = {'base_dir': BASE_DIR, 'template_dirs': []}
    for config_file in filter(None, path):
        config_path = config_dir / config_file
        config.update(_get_config(config_path))
    return config
