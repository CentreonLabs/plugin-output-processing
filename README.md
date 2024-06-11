# **P**lugin **O**utput **P**rocessing (POP)


This **new feature aims** at giving an **explanation** of a **plugin output** at the request of the user.

From a technical viewpoint, this **Python project** defines a **REST API**, designed with the **FastAPI** framework, taking as request a **plugin output** as well as some optional information on the monitored ressource where the output comes from, and giving a **relevant explanation in natural language** of it based on a underlying **LLM**. 

## Install & Start

1. Get source code.
```
git clone https://github.com/centreon/centreon-datascience.git
cd centreon-datascience/plugin-output-processing
```

2. Optionnaly, export your OpenAI key if you plan using OpenAI models.
```
export OPENAI_API_KEY=<KEY>
```

3. Optionnaly, export a configuration path
```
export POP_CONFIG_PATH=...          # configuration file path
````

Default values for this variable is shown in the table below.

| Variable         | Poetry                                 | Docker Compose           |
|------------------|----------------------------------------|--------------------------|
|`POP_CONFIG_PATH` | `ConfigPath('pop','centreon','.yaml')` | `/root/.pop/config.yaml` |

### Poetry

```
poetry install 
poetry run python3 -m plugin_output_processing.api
```

### Docker

```
docker compose up
```

## Use

1. Open your browser at the **URL** printed in the terminal.

2. Pass following information as **query parameters**.

| Parameter    | Type             | Default  | Description           |
|--------------|------------------|----------|-----------------------|
| `type`       | `host` `service` |          | Ressource type        |
| `name`       | `str`            | `n/a`    | Ressource name        |
| `output`     | `str`            | `n/a`    | Plugin output         |
| `description`| `str`            | `n/a`    | Ressource description |
 

## Settings

Path to the configuration file is printed when application start.
Configuration is loaded at each API call. Therefore, settings can be updated during runtime. 


| Parameter     | Type                         | Default                                     | Description        |
|---------------|------------------------------|---------------------------------------------|--------------------|
| `provider`    | `openai` `ollama`            | `openai`                                    | LLM provider       |
| `model`       | `str`                        | `gpt-4o`                                    | LLM model          |
| `temperature` | `[0-2]`                      | `1`                                         | LLM creativity     |
| `role`        | `str`                        | `You are a Centreon professional assistant` | LLM role           |
| `language`    | `English` `French` `Italian` | `English`                                   | Answer language    |
| `length`      | `int`                        | `100`                                       | Answer words limit |

The `model` parameter must be one of those available for the selected `provider`.
If not, the `model` is automatically set to the default provider model.

| Provider | Default          | Models                                         |
|----------|------------------|------------------------------------------------|
| `openai` | `gpt-4o`         | `gpt-3.5-turbo` `gpt-4` `gpt-4-turbo` `gpt-4o` |
| `ollama` | `ollama/mistral` | `ollama/mistral`                               |

### Local LLMs

Before choosing `ollama` as LLM provider, check that desired model is already installed with the followig command: 
```
ollama list
``` 

If not, install it with the command:
```
ollama pull <MODEL>
```
List of Ollama models [here](https://ollama.com/library).

## Example

### Host

#### Query
```
output: CRITICAL - 10.24.10.89: rta nan, lost 100%
name: siem-elastic-node-1-prod-root-ec2
type: host
```
#### Request URL   
```
http://127.0.0.1:8000/?output=CRITICAL%20-%2010.24.10.89%3A%20rta%20nan%2C%20lost%20100%25&name=siem-elastic-node-1-prod-root-ec2&description=n%2Fa&type=host
```

#### Prompt
```
Explain the following output coming from a Centreon plugin : CRITICAL - 10.24.10.89: rta nan, lost 100%.
Here are some informations about the monitored ressources :
Type: host
Name: siem-elastic-node-1-prod-root-ec2
Description: n/a
Describe mains reasons causing this output and suggest the better way to solve it.
Limit your answer to 100 words and answer in English.
```

#### Explanation
```
The output indicates that the host, 10.24.10.89 (siem-elastic-node-1-prod-root-ec2), is not reachable as Round Trip Average (RTA) time is not measurable (nan) and 100% packet loss. This might be caused by network issues, the host being down, or firewall settings blocking ICMP requests. Recommended solutions involve checking the network connectivity, ensuring the host is up and running, and verifying if firewall settings permit ICMP traffic.
```

### Service

#### Query
```
output: CRITICAL: No active swap
name: ACP-PASOL-601
description: swap
type: service
```
#### Request URL   
```
http://127.0.0.1:8000/?output=CRITICAL%3A%20No%20active%20sawp&name=ACP-PASOL-601&description=swap&type=service
```

#### Prompt
```
Explain the following output coming from a Centreon plugin : CRITICAL: No active sawp.
Here are some informations about the monitored ressources :
Type: service
Name: ACP-PASOL-601
Description: swap
Describe mains reasons causing this output and suggest the better way to solve it.
Limit your answer to 100 words and answer in French.
```

#### Explanation
```
Cette sortie indique qu'il n'y a pas de mémoire swap active sur le service ACP-PASOL-601. Cela pourrait être dû à une configuration incorrecte ou à une absence de mémoire swap assignée. Pour résoudre ce problème, vérifiez les paramètres de la mémoire swap de votre système. S'il n'y a pas de mémoire swap configurée, créez-en une. Si elle est configurée mais toujours inactive, essayez de la reactivez.
```

## Deployment

From the root of the project, execute the cmd `poe deploy` to build and publish the POP image on [Centreon Labs](https://hub.docker.com/u/centreondocker).

## Dependencies

- API
    - [FastAPI](https://fastapi.tiangolo.com/)
    - [Uvicorn](https://www.uvicorn.org/)
- LLM
    - [OpenAI](https://openai.com/)
    - [LiteLLM](https://litellm.ai/)
- Configuration
    - [PyYAML](https://pyyaml.org/)
    - [Pydantic](https://docs.pydantic.dev/latest/)
    - [ConfigPath](https://pypi.org/project/config-path/)
- Logging
    - [Loguru](https://loguru.readthedocs.io/en/stable/index.html)








