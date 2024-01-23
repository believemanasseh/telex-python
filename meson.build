project('telex',
          version: '0.1.0',
    meson_version: '>= 1.3.0',
  default_options: [ 'warning_level=2', 'werror=false', 'prefix=/home/manasseh/telex_python' ],
)

pymod = import('python')
py_installation = pymod.find_installation()

i18n = import('i18n')
gnome = import('gnome')

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)

i18n.gettext(meson.project_name())

telex_python_sources = [
  '__init__.py',
  'app.py',
  'window.py',
]

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
installdir = join_paths(pkgdatadir, 'telex_python/example')

py_installation.install_sources(telex_python_sources, install_dir: installdir)
