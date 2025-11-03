# SARA Timeseries

The **SARA Timeseries** provides an automated process to upload data to Omnia Timeseries API.
For more information about **Omnia Timeseries API**, see [Omnia](https://github.com/equinor/OmniaPlant)

## Required Environment Variables

| Env var                       | Description                    |
| ----------------------------- | ------------------------------ |
| SARA_TIMESERIES_CLIENT_SECRET | Omnia Timeseries Client Secret |

## Dependencies

The dependencies used for this package are listed in [`pyproject.toml`](pyproject.toml) and pinned in [`requirements.txt`](requirements.txt).
This ensures our builds are predictable and deterministic. This project uses `pip-compile` (from [`pip-tools`](https://github.com/jazzband/pip-tools))

```
pip-compile --output-file=requirements.txt pyproject.toml
```

To update the requirements to the latest versions, run the same command with the `--upgrade` flag:

```
pip-compile --output-file=requirements.txt pyproject.toml --upgrade
```

### Fast API App

App is running default at `localhost:8200/docs`

The app can be run locally through this command

```bash
python main.py
```

### Build the Docker image

```bash
docker build -t sara-timeseries .
```

Export env vars

```bash
export SARA_TIMESERIES_CLIENT_SECRET="<client-secret-to-timeseries-api>"
```

### Run the Docker image

```bash
docker run -p 8200:8200 --env-file ./.env sara-timeseries
```

### Running with Omnia Timeseries mock

You can find more information on running the mock [here](timeseries_mock/README.md).

For sara-timeseries you have to add this to your .env file:

```

USE_MOCK_TIMESERIES_API=true

```
