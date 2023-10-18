#!/usr/bin/env python3
import redis
r = redis.Redis(decode_responses=True)
r.ping()

data = {
    'hello': 'world',
    'lorem': 'ipsum'
}
#set multiple data
r.mset(data)
print(r.get('hello'))

prog_lang = ['python', 'Javascript', 'C++', 'Java']
#lpush - set list data type
r.lpush('languages', *prog_lang)

#lrange - traverse elements of a list
print(r.lrange('languages', 0, 2))
