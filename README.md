[![Python](https://img.shields.io/badge/Python-3%2E11-blue?logo=python)](https://devguide.python.org/versions/) &nbsp;
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green?logo=openai)](https://platform.openai.com/docs/models/gpt-4o) &nbsp;
[![Ollama](https://img.shields.io/badge/Local%20LLM-Ollama-green?logo=github)](https://github.com/ollama/ollama) &nbsp;
[![experimental](https://img.shields.io/badge/stability-experimental-red)](http://github.com/badges/stability-badges) &nbsp;
![interface](https://img.shields.io/badge/Interface-API-darkgreen?logo=fastapi)

# **P**lugin **O**utput **P**rocessing (POP)

Leverage LLMs to give an **explanation** of a Centreon **plugin output**.

## Examples

### Example 1 using OpenAI's GPT-4o

Output of a service monitoring a CPU:

> UNKNOWN: SNMP Table Request: Cant get a single value.

Explanation given using _GPT-4o_: 
> The output indicates that the Centreon plugin is unable to retrieve values from the SNMP table for CPU monitoring. Common causes include:
> 
>   1. Incorrect SNMP community string or credentials.\
>   2. SNMP service not running on the target device.
>   3. Network issues preventing SNMP communication.
>   4. Incorrect OIDs or SNMP version mismatch.
> 
> To resolve, verify SNMP configuration on the target device, ensure network connectivity, use correct SNMP community strings, and confirm matching SNMP versions between Centreon and the target device.

### Example 2 using Local model Qwen2-0.5B

Output of a service monitoring a database partioning: 

> CRITICAL: Partitions for table 'centreon_storage.data_bin' are not up to date (current retention forward in days: 0) - Partitions for table 'centreon_storage.logs' are not up to date (current retention forward in days: 0) - Partitions for table 'centreon_storage.log_archive_service' are not up to date (current retention forward in days: 0) - Partitions for table 'centreon_storage.log_archive_host' are not up to date (current retention forward in days: 0)

Explanation given using a local model _Qwen2-0.5B_:

> Output from a Centreon plugin is indicative of an issue where partitions for the table 'centreon_storage.data_bin' are no longer up to date, causing the retention forward rate to be set to zero. This can result from various reasons including:
>   * The storage provider does not support or implement the requested retention policies.
>   * There has been a failure in data backup and recovery processes.
>   * The database server is running out of memory.
> 
> Solving this issue might involve improving the implementation of these pieces of software such as:
>   * Adding more capacity to the storage servers
>   * Optimizing database processing to minimize memory usage
>   * Increasing the CPU load on the storage servers
>   * Reversing the retention forward rates if possible
> 
> In summary, it is recommended to identify and resolve the underlying issues first, then implementing solutions accordingly. This will improve the reliability of data backup and recovery processes without compromising storage performance or causing more downtime.

## Getting started

### Using docker and a local model

This method does not require any API key to be set or any configuration file to be provided.
A local model will be used to generate the explanations (Qwen2-0.5B) which can run on CPU.
At least 1GB of RAM is required to run the container.

```bash
git clone https://github.com/centreonlabs/plugin-output-processing.git

cd plugin-output-processing

docker compose --profile ollama up
```

After the container is up, you can try the API at `http://localhost:8000/docs`.
You can also use curl to try the API:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/explain?type=service&output=UNKNOWN%3A%20SNMP%20Table%20Request%3A%20Cant%20get%20a%20single%20value.&name=n%2Fa&description=cpu'
```

> [!TIP]
> The `--profile ollama` option is used to start the container with the local model.
> If you already have an ollama instance running, you can remove this option, just make sure `OLLAMA_HOST` is set.

### Using docker and OpenAI

This method requires an [OpenAI API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key) to be set as an environment variable: `OPENAI_API_KEY`.

```bash
export OPENAI_API_KEY=...

docker compose up
```

After the container is up, you can try the API the same way as the previous section.

> [!WARNING]
> Note that the OpenAI API is only used if no local model is found. 
> If you want to use the OpenAI API, you must unset the `OLLAMA_HOST` if it exists and can reach an ollama instance.

> [!CAUTHION]
> If you want to switch between providers (OpenAI to Ollama or vice versa), you must change the configuration file or removing it.

```bash
# Example to switch from OpenAI to Ollama

docker compose down

docker volume rm pop_pop

# We need to recreate the network because ollama will start first.
docker compose --profile ollama up --force-recreate
```

### Running the API locally

To run the API locally, you'll either need an OpenAI API key or a local model installed via [ollama](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key).

```bash
git clone
cd plugin-output-processing

# Create a virtual environment (need at least python 3.10)
python -m venv .venv
source .venv/bin/activate

# Install the dependencies
poetry install

# Run the API
poetry run uvicorn src.plugin_output_processing.api:app --reload
```

The API will be using the first model it can find on the ollama API, or the OpenAI API key if it doesn't find a local model.
See the next section to know how to configure the API to use a specific model.

## Usage

The API is a simple HTTP API that can be used to generate explanations for Centreon plugin outputs.
It can be accessed at `http://localhost:8000/docs`.

The API has a single endpoint that can be accessed with a GET request at `/explain`.
The endpoint requires the following query parameters:

| Parameter     | Type             | Default | Description           |
| ------------- | ---------------- | ------- | --------------------- |
| `type`        | `host` `service` |         | Ressource type        |
| `name`        | `str`            | `n/a`   | Ressource name        |
| `output`      | `str`            | `n/a`   | Plugin output         |
| `description` | `str`            | `n/a`   | Ressource description |


## Configuration

The API can be configured using a YAML file. 
The default configuration file is located at the root of the project and is named `config.yaml`.
The location of the configuration file can be changed by setting the environment variable `POP_CONFIG_PATH`.

If the configuration file is not found, the file will be created.
Here is an example of a configuration file:

```yaml
language: English
length: 100
model: gpt-4o
provider: openai
role: You are a Centreon professional assistant.
temperature: 1
```

| Parameter     | Type                         | Default                                     | Description        |
| ------------- | ---------------------------- | ------------------------------------------- | ------------------ |
| `provider`    | `openai` `ollama`            |                                             | LLM provider       |
| `model`       | `str`                        |                                             | LLM model          |
| `temperature` | `[0-2]`                      | `1`                                         | LLM creativity     |
| `role`        | `str`                        | `You are a Centreon professional assistant` | LLM role           |
| `language`    | `English` `French` `Italian` | `English`                                   | Answer language    |
| `length`      | `int`                        | `100`                                       | Answer words limit |

The `model` parameter must be one of those available for the selected `provider`.

For OpenAI, any models available on the [OpenAI API](https://platform.openai.com/docs/models) can be used (only text to text models).

For ollama, the models available can be listed with the command `ollama list`.
See the [ollama documentation](https://ollama.com/) for more information to install or install a model.

_NOTES_: If the configuration is changed, the API must be restarted to apply the changes.
