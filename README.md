# SixGPT Miner

Miner for the SixGPT Synthetic Data Generation DLP

# About

SixGPT is a decentralized synthetic data generation platform built on the Vana network. We empower users by giving them ownership of their data and enabling them to earn from it.

The SixGPT Miner is a software package which allows users to contribute data they generate for wikipedia question-answer based tasks to the network for rewards.
In the future, we will support other tasks such as chatbot conversations, image captioning, etc.

# Credentials

SixGPT uses two credentials to perform mining on Vana:

1. OpenAI api key, for access to the OpenAPI API
2. Google OAUTH, for storing your mined data in Google Drive.

# Install

## Prerequisites

SixGPT uses several dependencies to operate.

- Python 3.12
- Poetry

```shell
brew install python
curl -sSL https://install.python-poetry.org | python3 -
```

## Quick Start

```shell
git clone https://github.com/sixgpt/minercli.git
cd minercli
source setup.sh
```

You should now have access to the `sixgpt` cli command.

# Interface

The interface can be accessed via the CLI at `./bin/sixgpt`

## Mining

By default, miner runs as a background daemon.

#### Start Mining

```shell
sixgpt mine start
```

| Flag | Description                           |
| ---- | ------------------------------------- |
| -b   | Run the miner in a background process |

#### Stop Mining

```shell
sixgpt mine stop
```

#### See Mining Logs

```shell
sixgpt mine logs
```

## Auth

### Google Drive

#### Login to Drive

```shell
sixgpt auth drive login
```

#### Logout to Drive

```shell
sixgpt auth drive logout
```

### OpenAI

#### Set OpenAI API Key

```shell
sixgpt auth openai login
```

#### Reset OpenAI API Key

```shell
sixgpt auth openai logout
```

## Misc

#### Update the SixGPT CLI

```shell
sixgpt update
```

#### Check the SixGPT CLI version

```shell
sixgpt --version
```
