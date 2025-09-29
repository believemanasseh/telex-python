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
pngs = [
  ('@0@.upvote.png').format(application_id),
  ('@0@.downvote.png').format(application_id),
  ('@0@.profile.png').format(application_id),
  ('@0@.search.png').format(application_id),
  ('@0@.reload.png').format(application_id),
  ('@0@.logo.png').format(application_id),
  ('@0@.sort-down.png').format(application_id),
  ('@0@.arrow-pointing-left.png').format(application_id),
  ('@0@.homepage.png').format(application_id),
  ('@0@.create-post.png').format(application_id),
  ('@0@.close.png').format(application_id),
  ('@0@.delete.png').format(application_id),
]

foreach png : pngs
  install_data(
    join_paths(fourty_eight_pixels_dir, png),
    install_dir: join_paths(get_option('datadir'), 'icons', fourty_eight_pixels_dir),
  )
endforeach