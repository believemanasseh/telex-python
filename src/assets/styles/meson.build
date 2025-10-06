pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'telex_python/assets/styles')

css_source_files = [
    'home.css',
    'auth.css',
    'post_detail.css',
    'profile.css',
    'new_post.css',
    'search.css',
]

install_data(css_source_files, install_dir: moduledir)