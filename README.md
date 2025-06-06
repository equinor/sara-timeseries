# SARA Timeseries

The **SARA Timeseries** provides an automated process to upload data to Omnia Timeseries API. For more information about **Omnia Timeseries API**, see [Omnia](https://github.com/equinor/OmniaPlant)

## Required Environment Variables

| Env var                  | Description                    |
| ------------------------ | ------------------------------ |
| TIMESERIES_CLIENT_ID     | Omnia Timeseries Client ID     |
| TIMESERIES_CLIENT_SECRET | Omnia Timeseries Client Secret |
| TIMESERIES_TENANT_ID     | Omnia Timeseries Tenant ID     |

## Dependencies

The dependencies used for this package are listed in `pyproject.toml` and pinned in `requirements.txt`. This ensures our builds are predictable and deterministic. This project uses `pip-compile` (from [`pip-tools`](https://github.com/jazzband/pip-tools)) for this:

```
pip-compile --output-file=requirements.txt pyproject.toml
```

To update the requirements to the latest versions, run the same command with the `--upgrade` flag:

```
pip-compile --output-file=requirements.txt pyproject.toml --upgrade
```

### Fast API App

App is running default at `localhost:8000/docs`

### Build the Docker image

```bash
docker build -t sara-imeseries:test .
```

Export env vars

```bash
export TIMESERIES_CLIENT_ID="<client-id-to-timeseries-api>"
export TIMESERIES_CLIENT_SECRET="<client-secret-to-timeseries-api>"
export TIMESERIES_TENANT_ID="<tenant-id-to-timeseries-api>"
```
