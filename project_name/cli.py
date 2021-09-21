import typer
import uvicorn
from sqlmodel import Session, select

from .app import app
from .config import settings
from .db import create_db_and_tables, engine
from .models.content import Content
from .security import User

cli = typer.Typer(name="project_name API")


@cli.command()
def run(
    port: int = settings.server.port,
    host: str = settings.server.host,
    log_level: str = settings.server.log_level,
    reload: bool = settings.server.reload,
):  # pragma: no cover
    """Run the API server."""
    uvicorn.run(
        "project_name.app:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )


@cli.command()
def create_user(username: str, password: str, superuser: bool = False):
    """Create user"""
    create_db_and_tables(engine)
    with Session(engine) as session:
        user = User(username=username, password=password, superuser=superuser)
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {username} user")
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
        "select": select,
        "session": Session(engine),
        "Content": Content,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(argv=[], user_ns=_vars)
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()
