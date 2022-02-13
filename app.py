import sys

from burgerzilla import create_app

init_config = False
if sys.argv[1:] is not None:
    if sys.argv[1:][0] == "init-config":
        init_config = True

if init_config:
    print("config.yml has been initialized.")
else:
    if __name__ == '__main__':
        app = create_app()

        app.run()
