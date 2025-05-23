pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'telex_python')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3.12').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'telex.in',
  output: 'telex',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
)

telex_python_sources = [
  '__init__.py',
  'app.py',
  'store.py',
  'services.py',
]
install_data(telex_python_sources, install_dir: moduledir)

subdir('windows')
subdir('utils')
subdir('assets')