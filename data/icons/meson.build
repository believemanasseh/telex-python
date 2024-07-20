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

fourty_eight_pixels_dir = join_paths('hicolor', '48x48', 'apps')
install_data(
  join_paths(fourty_eight_pixels_dir, 'upvote-btn.png'),
  install_dir: join_paths(get_option('datadir'), 'icons', fourty_eight_pixels_dir),
)
install_data(
  join_paths(fourty_eight_pixels_dir, 'downvote-btn.png'),
  install_dir: join_paths(get_option('datadir'), 'icons', fourty_eight_pixels_dir),
)