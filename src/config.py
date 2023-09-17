import os
from dotenv import load_dotenv


class Config(object):
    def __init__(self):
        load_dotenv()
        self.env_variables = os.environ

    def getenv(self, variable_name, default=None) -> str:
        return self.env_variables.get(variable_name, default)
