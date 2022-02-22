APP_NAME = "pixync"
APP_DESC = "distributed digital asset management system for photographers"
APP_VERSION = "v1.1"

class AppInfo:

    @property
    def name(self) -> str:
        return APP_NAME

    @property
    def description(self):
        return APP_DESC

    @property
    def version(self):
        return APP_VERSION