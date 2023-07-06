
[![Unit tests](https://github.com/kaveryanovGFL/fuzzy_back/actions/workflows/test_modules.yml/badge.svg?branch=develop&event=push)](https://github.com/kaveryanovGFL/fuzzy_back/actions/workflows/test_modules.yml)
# fuzzy_back
<p align="center">
  <a href="https://fastapi.tiangolo.com"><img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI"></a>
</p>

# Table of Contents

* [Installation](#installation)
* [Usage](#usage)


## Installation

1. Install the latest <a href="https://www.python.org/downloads/">python</a> package from

2. Install the <a href="https://www.docker.com/">docker</a>

3. In terminal open project folder and run
```bash
git clone  https://github.com/kaveryanovGFL/fuzzy_back.git
```
4.  Build docker images
```bash
docker-compose up --build
```
## Usage
From command line run in your environment run. Make sure you in `environment`
<br>
<b>Run db</b> option `up`, `down`, `restart`
```bash
docker-compose up mongo
```
<b>Run server</b> option `up`, `down`, `restart`
```bash
docker-compose up backend
```
<b>Run celery beat & worker</b> option `up`, `down`, `restart`
```bash
docker-compose up crontab
```
<b>Run all</b> option `up`, `down`, `restart`
```bash
docker-compose up
```

Open url http://localhost:8000/docs
