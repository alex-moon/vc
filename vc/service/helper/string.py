from datetime import timedelta


class StringHelper:
    @classmethod
    def timedelta(cls, d: timedelta):
        s = d.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{hours}h {minutes}m {seconds}s'.format(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
