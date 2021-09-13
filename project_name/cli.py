import typer
import uvicorn
from sqlmodel import Session

from .app import app
from .config import settings
from .db import engine
from .models.user import User

cli = typer.Typer(name="project_name API")


@cli.command()
def run(
    port: int = settings.port,
    host: str = settings.host,
    log_level: str = settings.log_level,
):  # pragma: no cover
    """Run the API server."""
    uvicorn.run(app, host=host, port=port, log_level=log_level)


@cli.command()
def create_user(name: str, password: str, superuser: bool = False):
    """Create user"""
    with Session(engine) as session:
        user = User(name=name, password=password, superuser=superuser)
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {name} user")
        return user


@cli.command()
def shell():  # pragma: no cover
    """Opens an interactive shell with objects auto imported"""
    _vars = {
        "app": app,
        "settings": settings,
        "User": User,
        "engine": engine,
        "cli": cli,
        "create_user": create_user,
    }
    try:
        from IPython import start_ipython

        start_ipython(argv=[], user_ns=_vars)
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()
