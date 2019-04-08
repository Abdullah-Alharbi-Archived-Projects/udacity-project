#!/usr/bin/env python3
from itemcatalog import *
from itemcatalog.models import User, Category, Item
from itemcatalog import routes

# this file will run the project
# use python3 run.py
# and please make sure to
# use this version of python: 3.5.2

if __name__ == "__main__":
    # please check config.json
    app.run(host=config["host_address"],
            port=config["port"], debug=config["debug_mode"])
