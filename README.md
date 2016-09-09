[![Code Climate](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/badges/gpa.svg)](https://codeclimate.com/github/TheSoftwareFactory/experiment-server)

# Experiment-server

A simple REST API server for providing runtime configurations for applications and receiving usage-related event data.

###Getting Started
---------------

Clone this repository

- export a virtual env
`export VENV=~/env`

- Setup the environment (from the project root folder):
`./scripts/setup-environment.sh`

- Initialize database:
`$VENV/bin/initialize_Experiment-server_db development.ini`

- Start the local server:
`$VENV/bin/pserve development.ini`

- Install hooks (from the project root folder):
`./scripts/install-precommit-hooks.sh`


Run tests:

`$VENV/bin/py.test experiment_server/tests.py`

###Trying the REST API using `curl`

Creating a new experiment:

    $ curl -H "Content-Type: application/json" -X POST -d '{"name": "My First Experiment", "experimentgroups": [{"name":"Group A", "configurations":[{"key":"key A", "value":4}]}, {"name": "Group B", "configurations":[{"key":"key B", "value":5}]}]}' http://localhost:6543/experiments

Deleting an experiment:

    $ curl -H "Content-Type: application/json" -X DELETE -d '' http://localhost:6543/experiments/1

###Work flow

- Take a task from Trello (card)
- Create a new branch for it `git branch <task_name>`
- Start working only that branch
- Rebase often with the master `git checkout master` `git pull` `git checkout <task_name>` `git rebase master`
- Fix all the conflicts
- TEST!
- When rebasing is done. Save your work globally `git push origin <task_name>`
- When you feel that you would like the whole team get your code: Make a pull-request
- Assign somebody to code review your work
- When the code review is done merge the branch to master via GitHub.com

