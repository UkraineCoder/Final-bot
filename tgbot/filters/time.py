from aiogram.dispatcher.filters import BoundFilter


class HourFilter(BoundFilter):
    async def check(self, obj):
        hour = obj.text

        try:
            hour_int = int(hour)
            if 0 <= hour_int <= 23:
                return True
        except Exception:
            return False


class MinuteFilter(BoundFilter):
    async def check(self, obj):
        minute = obj.text

        try:
            minute_int = int(minute)
            if 0 <= minute_int <= 59:
                return True
        except Exception:
            return False
