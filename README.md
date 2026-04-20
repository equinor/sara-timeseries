# SARA Timeseries

The **SARA Timeseries** provides an automated process to upload data to Omnia Timeseries API.
For more information about **Omnia Timeseries API**, see [Omnia](https://github.com/equinor/OmniaPlant)

## Dependencies

The dependencies used for this package are listed in [`pyproject.toml`](pyproject.toml) and pinned in [`uv.lock`](uv.lock).
This ensures our builds are predictable and deterministic. This project uses [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
uv lock
```

To update the dependencies to the latest versions, run:

```bash
uv lock --upgrade
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
Remember to export the environment variables. 

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
