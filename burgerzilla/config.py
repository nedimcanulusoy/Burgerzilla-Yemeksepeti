import os, yaml, secrets
from os.path import exists

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    config_path = os.getcwd() + "/config.yml"
    file_exists = exists(config_path)

    if not file_exists:
        data = dict(
            secret=secrets.token_hex(32),

            database=dict(
                user='fill-here-with-your-data',
                db='fill-here-with-your-data',
                password='fill-here-with-your-data',
                host='fill-here-with-your-data',
                port='fill-here-with-your-data',
            )
        )

        with open(config_path, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

    stream = open(config_path, 'r')
    config = yaml.load(stream, Loader=yaml.FullLoader)

    USER_ENABLE_EMAIL = False
    SECRET_KEY = config["secret"]
    JWT_SECRET_KEY = config["secret"]
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{config["database"]["user"]}:' \
                              f'{config["database"]["password"]}' \
                              f'@{config["database"]["host"]}/{config["database"]["db"]}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    # SWAGGER_UI_DOC_EXPANSION = "list"
