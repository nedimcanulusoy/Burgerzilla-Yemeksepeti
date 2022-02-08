import os, yaml

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    stream = open(os.getcwd() + "/config.yml", 'r')
    config = yaml.load(stream, Loader=yaml.FullLoader)

    SECRET_KEY = config["secret"]
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{config["database"]["user"]}:' \
                           f'{config["database"]["password"]}' \
                           f'@{config["database"]["host"]}/{config["database"]["db"]}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
