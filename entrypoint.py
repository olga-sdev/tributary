import json
import redis as redis
from flask import Flask, request
from loguru import logger


HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

# create a Flask server, and allow us to interact with it using the app variable
app = Flask(__name__)


@app.route('/record', methods=['POST'])
def record_engine_temperature():
    """
    Endpoint accepts POST requests, and is reachable from the /record endpoint

    get_json() -> extracts the JSON payload from the request
    redis.Redis() -> open up a connection to the Redis database, which is running in a different container
    database.lpush -> storing engine temperature readings in a Redis list,
    database.rpop -> keeping track of the 10 most recent values, and discarding old ones as new ones appear

    :return: {"success": True}, 200
    """
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    return {"success": True}, 200


@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    """
    Collect temperature data from engine

    redis.Redis -> connect to Redis DB
    database.lrange -> get temperature values
    calculate average_engine_temperature and get the current temperature

    :return: current_engine_temperature and average_engine_temperature, success status code 200
    """
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list contains values: {engine_temperature_values}")

    average_engine_temperature = sum([float(t) for t in engine_temperature_values]) / len(engine_temperature_values)
    logger.info(f"average engine temperature: {average_engine_temperature}")
    logger.info(f"current engine temperature: {engine_temperature_values[0]}")

    result = {
        "current_engine_temperature": float(engine_temperature_values[0]),
        "average_engine_temperature": average_engine_temperature
    }

    logger.info(f"collect request successful")
    return result, 200
