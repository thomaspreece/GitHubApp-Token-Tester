# GitHub App Token Tester
When you have a GitHub App installation token (starting with `ghs_`, see [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github#githubs-token-formats)) then there isn't an endpoint that will tell you which permissions the token has. The purpose of this repo is to provide a tool that makes a set of requests to GitHub to test the exact permissions of the token. 

Notes:
- This tool isn't designed stealthy. All requests made will appear in GitHub audit logs. Also, some requests have to test write permissions so will make changes
- Not all GitHub permissions are implemented by this tool yet. 

## Requirements
To use this tool you need one of the following:
- A `ghs_` token (note these tokens are only valid for 1 hour so please take this into account when testing) OR
- A GitHub App private key + app id + app instation id

You'll also need to install the python depenedencies in `requirements.txt`

## Use

- Copy `.env.example` to `.env`
- Fill in `.env` with required values
- If using `ghs_` token then run `python3 ./test_app_permissions.py`, otherwise if using GitHub App private key then run `python3 ./app_pem_harness.py`
- See terminal output and `permissions.csv` for results of run.