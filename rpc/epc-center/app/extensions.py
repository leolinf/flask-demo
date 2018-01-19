# -*- coding = utf-8 -*-

import functools
import logging

from flask_cache import Cache

from app import Config


class CustomCache(Cache):

    def memoize(self, timeout=None, make_name=None, unless=None):
        def memoize(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):

                try:
                    logger_name = args[0]
                except Exception:
                    logger_name = "memoize"

                logger = logging.getLogger(logger_name)
                #: bypass cache
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)

                try:
                    cache_key = decorated_function.make_cache_key(f, *args, **kwargs)
                    rv = self.cache.get(cache_key)
                except Exception:
                    logger.exception("Exception possibly due to cache backend.")
                    return f(*args, **kwargs)

                if rv is None:
                    rv = f(*args, **kwargs)
                    from app.common.helper import check_whether_cache_from_response
                    if check_whether_cache_from_response(rv):
                        try:
                            self.cache.set(cache_key, rv,
                                           timeout=decorated_function.cache_timeout)
                        except Exception:
                            logger.exception("Exception possibly due to cache backend.")
                else:
                    logger.info("Get data from cache.")

                return rv

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = self._memoize_make_cache_key(
                make_name, decorated_function)
            decorated_function.delete_memoized = lambda: self.delete_memoized(f)

            return decorated_function
        return memoize


cache = CustomCache(config={
    "CACHE_TYPE": Config.CACHE_TYPE,
    "CACHE_KEY_PREFIX": Config.CACHE_KEY_PREFIX,
    "CACHE_REDIS_URL": Config.CACHE_REDIS_URL,
})
