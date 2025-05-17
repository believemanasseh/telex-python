"""Application-level constant variables."""

from enum import IntEnum


class Seconds(IntEnum):
	"""Time (secs) constants for Reddit post submissions."""

	MINUTE = 60
	HOUR = 3600
	DAY = 86400
	WEEK = 604800


class SortType(IntEnum):
	"""Sort type constants for Reddit posts."""

	BEST = 0
	NEW = 1
	HOT = 2
	TOP = 3
	RISING = 4
