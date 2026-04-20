# Omnia Timeseries Mock

The **Omnia Timeseries Mock** provides an Http Client and a Mock server that mocks the behavior of Http Requests to the Omnia Timeserie API.
This mock can be used to facilitate local testing during development.

## Dependencies

The dependencies used for this package are listed in [`pyproject.toml`](timeseries_mock/pyproject.toml) and pinned in [`uv.lock`](timeseries_mock/uv.lock).
This ensures our builds are predictable and deterministic. This project uses [uv](https://docs.astral.sh/uv/) for dependency management.
From the `timeseries_mock` folder, run the following:

```
uv lock
```

To update the dependencies to the latest versions, run:

```
uv lock --upgrade
```

## Run

```
python omnia_timeseries_mock.py
```
