pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'telex_python/windows')

telex_python_sources = [
    '__init__.py',
    'onboarding.py'
]

install_data(telex_python_sources, install_dir: moduledir)