import os

from dynaconf import Dynaconf

HERE = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix="project_name",
    preload=[os.path.join(HERE, "default.toml")],
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["development", "production", "testing"],
    env_switcher="project_name_env",
    load_dotenv=False,
)


"""
# How to use this application settings

```
from project_name.config import settings
```

## Acessing variables

```
settings.get("SECRET_KEY", default="sdnfjbnfsdf")
settings["SECRET_KEY"]
settings.SECRET_KEY
settings.db.uri
settings["db"]["uri"]
settings["db.uri"]
settings.DB__uri
```

## Modifying variables

### On files

settings.toml
```
[development]
KEY=value
```

### As environment variables
```
export PROJECT_NAME_KEY=value
export PROJECT_NAME_KEY="@int 42"
export PROJECT_NAME_KEY="@jinja {{ this.db.uri }}"
export PROJECT_NAME_DB__uri="@jinja {{ this.db.uri | replace('db', 'data') }}"
```

### Switching environments
```
PROJECT_NAME_ENV=production project_name run
```

Read more on https://dynaconf.com
"""
