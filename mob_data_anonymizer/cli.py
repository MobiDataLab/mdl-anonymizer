import typer

from typing import Optional
from mob_data_anonymizer import __app_name__, __version__, DEFAULT_PARAMETERS_FILE, ERRORS, SUCCESS
from mob_data_anonymizer.anonymizer import check_parameters_file, anonymizer

app = typer.Typer()


@app.command()
def anonymize(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-pl",
            prompt="Anonymization parameters file location"
        ),
) -> None:
    code = check_parameters_file(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Anonymization failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        anonymizer(parameters_file)

@app.command()
def synthetic_generation(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-pl",
            prompt="Anonymization parameters file location"
        ),
) -> None:
    code = check_parameters_file(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Synthetic generation failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")

        raise typer.Exit()


@app.callback()
def main(
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=_version_callback,
            is_eager=True,
        )
) -> None:
    return
