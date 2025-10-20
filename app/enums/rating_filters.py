from enum import Enum


class RatingFilters(Enum):
    RECENT = "recent"
    OLDEST = "oldest"
    BEST = "best"
    WORST = "worst"
