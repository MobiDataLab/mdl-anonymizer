import typer

from typing import Optional

from mob_data_anonymizer.client import filter_data, tasks_manager, anonymizer, analyzer, compute_measures
from mob_data_anonymizer import __app_name__, __version__, DEFAULT_PARAMETERS_FILE, ERRORS, SUCCESS

app = typer.Typer()


@app.command()
def anonymize(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-f",
            prompt="Anonymization parameters file location"
        ),
) -> None:
    code = anonymizer.check_parameters_file(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Anonymization failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        anonymizer.anonymizer(parameters_file)


@app.command()
def anonymize_api(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-f",
            prompt="Anonymization parameters file location"
        ),
) -> None:
    code = anonymizer.check_parameters_file_api(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Anonymization failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        anonymizer.anonymizer_api(parameters_file)


@app.command()
def analysis(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-f",
            prompt="Analysis parameters file location"
        ),
) -> None:
    code = analyzer.check_parameters_file(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Analysis failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        analyzer.run_analysis(parameters_file)


@app.command()
def analysis_api(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-f",
            prompt="Analysis parameters file location"
        ),
) -> None:
    code = analyzer.check_parameters_file_api(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Analysis failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        analyzer.run_analysis_api(parameters_file)


@app.command()
def measures(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-f",
            prompt="Measures parameters file location"
        ),
) -> None:
    code = compute_measures.check_parameters_file(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Measures failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        compute_measures.compute_measures(parameters_file)


@app.command()
def measures_api(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-f",
            prompt="Measures parameters file location"
        ),
) -> None:
    code = compute_measures.check_parameters_file_api(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Measures failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        compute_measures.compute_measures_api(parameters_file)


@app.command()
def filter(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-f",
            prompt="Filter parameters file location"
        ),
) -> None:
    code = filter_data.check_parameters_file(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Filter failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        filter_data.filter_dataset(parameters_file)


@app.command()
def filter_api(
        parameters_file: str = typer.Option(
            str(DEFAULT_PARAMETERS_FILE),
            "--parameters_file",
            "-f",
            prompt="Filter parameters file location"
        ),
) -> None:
    code = filter_data.check_parameters_file_api(parameters_file)
    if code != SUCCESS:
        typer.secho(
            f'Filter failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )

        raise typer.Exit(1)
    else:
        filter_data.filter_dataset_api(parameters_file)


@app.command()
def get_task(
        task_id: str = typer.Option(
            ...,
            "--task_id",
            "-t",
            prompt="Task id"
        ),
) -> None:
    tasks_manager.request_return_task(task_id)


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
