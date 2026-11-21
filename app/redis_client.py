#Created a new file in app/ because we wanted a reusable file


import os
import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_URL=os.getenv("REDIS_URL")

redis_client=redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,  #This timeout setting prevents requests from hanging indefinitely if Redis becomes unresponsive
    socket_timeout=2
)
#Creates a redis client using the URL in .env file

#decode_response=True: Redis stores data as bytes internally
#without this option: a retureved value might look like: b'https://google.com'

#with that turned on, iti is much easier ot work with 