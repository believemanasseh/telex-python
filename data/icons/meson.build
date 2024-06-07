application_id = 'xyz.daimones.Telex'

scalable_dir = join_paths('hicolor', 'scalable', 'apps')
install_data(
  join_paths(scalable_dir, ('@0@.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', scalable_dir),
)

symbolic_dir = join_paths('hicolor', 'symbolic', 'apps')
install_data(
  join_paths(symbolic_dir, ('@0@-symbolic.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', symbolic_dir),
)

fourty_eight_pixels_dir = join_paths('hicolor', '48x48')
png_icons = [
  join_paths(fourty_eight_pixels_dir, 'arrow-up.png'),
  join_paths(fourty_eight_pixels_dir, 'arrow-down.png'),
]
install_data(
  sources: png_icons,
  install_dir: join_paths(get_option('datadir'), 'icons', fourty_eight_pixels_dir),
)