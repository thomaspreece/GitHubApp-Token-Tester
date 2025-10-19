import os
from github import Github, Auth
from dotenv import load_dotenv

load_dotenv() 

## General Authentication Flow
# JWT Created using Private Key
# JWT used to access GitHub Apps API.
# - Call API to get installation id for an integration(app) id on a repo.
# - Use JWT & installation id to request access token valid for 1hr

## Access Token vs JWT
# Access Tokens can access a long list of endpoints:
# https://docs.github.com/en/rest/overview/endpoints-available-for-github-apps
# and be used with git directly: `git clone https://x-access-token:<token>@github.com/owner/repo.git`
# JWT tokens minted by the private key can only access app based endpoints:
# https://docs.github.com/en/rest/apps

GH_APP_ID = int(os.getenv("GH_APP_ID"))
GH_INSTALLATION_ID = int(os.getenv("GH_INSTALLATION_ID"))

GH_APP_PATH = os.getenv("GH_APP_PATH", "app.private-key.pem")

with open(os.path.normpath(os.path.expanduser(GH_APP_PATH)), 'r') as cert_file:
    app_key = cert_file.read()

auth = Auth.AppAuth(GH_APP_ID, app_key)
installation_auth = auth.get_installation_auth(GH_INSTALLATION_ID)
Github(auth=installation_auth) # Required to get installation_auth token below

os.environ["GH_APP_KEY"] = installation_auth.token

import test_app_permissions




