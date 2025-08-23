from wassden.clis.core import app
from wassden.utils.dev_gate import is_dev_mode

if is_dev_mode():
    from wassden.clis.experiment import experiment_app

    app.add_typer(experiment_app, name="experiment")


if __name__ == "__main__":
    app()
