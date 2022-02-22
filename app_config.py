from inspect import Attribute
import os
import yaml

CONFIG_FILE_NAME = 'config.yaml'
DB_FILE_NAME = 'activity.db'
DELETE_LOG_NAME = "delete.log"
IMPORT_LOG_NAME = "import.log"

class AppConfig:

    def __init__(self, appInfo):
        self.config_file_dir = "." + appInfo.name + os.path.sep
        self._global_config_file_path = self.get_global_config_file_path()
        self._global_config_settings = self.read_global_settings()

    @property
    def dir(self):
        return self.config_file_dir

    @property
    def file_name(self):
        return CONFIG_FILE_NAME

    @property
    def file_path(self):
        return self.config_file_dir + CONFIG_FILE_NAME

    @property
    def db_file_path(self):
        return self.config_file_dir + DB_FILE_NAME

    @property
    def delete_log_path(self):
        return self.config_file_dir + DELETE_LOG_NAME

    @property
    def import_log_path(self):
        return self.config_file_dir + IMPORT_LOG_NAME

    @property
    def global_config_file_path(self):
        return self._global_config_file_path

    @property
    def global_config_settings(self):
        return self._global_config_settings

    def get_global_config_file_path(self):
        config_file_global = os.path.expanduser('~') + os.path.sep + self.file_path
        if not os.path.exists(config_file_global):
            config_file_global = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + self.file_name

        if not os.path.exists(config_file_global):
            return None
        
        return config_file_global
    
    def read_global_settings(self):
        with open(self._global_config_file_path) as file:
            return yaml.load(file, Loader=yaml.FullLoader)