# Omnia Timeseries Mock

The **Omnia Timeseries Mock** provides an Http Client and a Mock server that mocks the behavior of Http Requests to the Omnia Timeserie API.
This mock can be used to facilitate local testing during development.

## Dependencies

The dependencies used for this package are listed in [`pyproject.toml`](timeseries_mock/pyproject.toml) and pinned in [`requirements.txt`](timeseries_mock/requirements.txt).
This ensures our builds are predictable and deterministic. This project uses `pip-compile` (from [`pip-tools`](https://github.com/jazzband/pip-tools))
From the `timeseries_mock` folder, run the following:

```
pip-compile --output-file=requirements.txt pyproject.toml
```

To update the requirements to the latest versions, run the same command with the `--upgrade` flag:

```
pip-compile --output-file=requirements.txt pyproject.toml --upgrade
```

## Run

```
python omnia_timeseries_mock.py
```
