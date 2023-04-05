# GitHub Follower Bot


[![Python version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/pygithub.svg)](https://badge.fury.io/py/pygithub)

A Python bot designed to follow and unfollow users on GitHub using the GitHub REST API. 



## Getting Started


You can install the required libraries using pip:

`pip install PyGithub requests`

<br>

### Installation

1. Create a virtual environment and activate it:
```
python3 -m venv env
source env/bin/activate
```
2. Install the required libraries:
`pip install -r requirements.txt`

<br>

### Usage

To use the bot, run the following command:

`python followers.py -t <access_token> -u <userfile> -m <mode>`

- `-t`, `--token`: Access token for the GitHub API.
- `-u`, `--userfile`: Path to a file containing a list of usernames to follow/unfollow.
- `-m`, `--mode`: Mode of operation. Must be either "follow" or "unfollow".


Additional options:

- `-v`, `--verbose`: Verbose output.
- `-s`, `--silent`: Silent mode (only output successful attempts).
- `-h`, `--help`: Show help message and exit.
