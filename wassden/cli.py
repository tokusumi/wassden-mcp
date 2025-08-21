from wassden.clis.core import app
from wassden.clis.experiment import experiment_app
from wassden.utils.dev_gate import is_dev_mode

if is_dev_mode():
    app.add_typer(experiment_app, name="experiment")


if __name__ == "__main__":
    app()
