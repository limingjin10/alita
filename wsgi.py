import os
import inc

config_file = os.environ.get("ALITA_CONFIG", "../config/alita/prod.py")
application = inc.create_app(config_file)

