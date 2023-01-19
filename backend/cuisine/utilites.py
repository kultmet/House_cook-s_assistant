# import redis # сторонняя
from redis import Redis

redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)
print(redis.get('fuck'))