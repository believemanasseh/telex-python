pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'telex_python/windows')

telex_python_sources = [
    '__init__.py',
    'auth.py',
    'home.py',
    'post_detail.py',
    'titlebar_controller.py',
    'preferences.py',
    'profile.py'
]

install_data(telex_python_sources, install_dir: moduledir)