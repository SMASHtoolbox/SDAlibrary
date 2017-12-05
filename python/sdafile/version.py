major = 0
minor = 3
patch = 0
dev = True

version = '{major}.{minor}.{patch}{dev}'.format(
    major=major, minor=minor, patch=patch, dev='.dev0' if dev else ''
)
