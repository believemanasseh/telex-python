pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'telex_python/utils')

telex_python_sources = [
    '__init__.py',
    'common.py',
    'constants.py',
    'services.py',
]

install_data(telex_python_sources, install_dir: moduledir)