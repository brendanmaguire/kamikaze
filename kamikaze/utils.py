import time

DEFAULT_REDIS_KEY = 'kamikaze'


class Package(object):
    """
    Instances of this class store the values of a package on the kamikaze queue

    This item should be treated as immutable
    """

    def __init__(self, payload, expire_time, score):
        self._payload = payload
        self._expire_time = None if expire_time is None else float(expire_time)
        self._score = score

    def __repr__(self):
        return (
            'Package(payload={payload},score={score},expire_time={expire_time}'
            ')'.format(payload=self.payload, score=self.score,
                       expire_time=self.expire_time))

    @property
    def payload(self):
        return self._payload

    @property
    def expire_time(self):
        return self._expire_time

    def ttl(self, now):
        return self.expire_time - now

    def expired(self, now):
        return self.expire_time is not None and self.expire_time < now

    @property
    def raw_entry(self):
        expire_time = '' if self._expire_time is None else self._expire_time
        return '{expire_time}:{payload}'.format(
            expire_time=expire_time, payload=self._payload)

    @property
    def score(self):
        return self._score

    def __lt__(self, other):
        """
        The higher the score, the higher the items value
        """
        return self.score < other.score

    @staticmethod
    def value_to_expire_time_and_payload(value):
        return value.split(':')


def extract_package(entry):
    value, score = entry
    try:
        # Convert byte variable to string
        value = value.decode()
    except AttributeError:
        pass

    expire_time, payload = Package.value_to_expire_time_and_payload(value)

    if expire_time.strip() != '':
        expire_time = float(expire_time)
    else:
        expire_time = None

    return Package(
        payload=payload,
        expire_time=expire_time,
        score=score)


def create_package_with_ttl(payload, ttl, score, now=None):
    now = now or time.time()
    expire_time = now + ttl

    return Package(
        payload=payload,
        expire_time=expire_time,
        score=score)
