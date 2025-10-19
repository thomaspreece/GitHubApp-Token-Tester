import requests
import os 
from dotenv import load_dotenv
import json 
import csv 

load_dotenv() 

GH_APP_KEY = os.getenv("GH_APP_KEY")

GH_REPO_NAME = os.getenv("GH_REPO_NAME")
GH_REPO_ORG = os.getenv("GH_REPO_ORG")

def make_github_api_request(request_data):
    data = request_data["data"]
    method = request_data["method"]
    path = request_data["url"]
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GH_APP_KEY}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if data:
        response = requests.request(
            method, 
            "https://api.github.com"+path, 
            headers=headers,
            data=json.dumps(data)
        )
    else:
        response = requests.request(
            method, 
            "https://api.github.com"+path, 
            headers=headers
        )

    return response

def write_results(results_writer, request_data, response, notes="", success_codes=["200","201"]):
    permission = request_data["permission"]
    data = request_data["data"]
    method = request_data["method"]
    path = request_data["url"]

    results_writer.writerow([
        permission,
        str(response.status_code), 
        notes,
        f"{method}: {path}",
        data,
        response.text
    ])

    if str(response.status_code) in success_codes:
        print(f"SUCCESS: {permission}")
    else:
        print(f"FAIL: {permission}")


results_csv = open('permissions.csv', mode='w')
results_writer = csv.writer(results_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

results_writer.writerow([
    "permission",
    "success", 
    "notes",
    "request_url",
    "request_data",
    "response_raw"
])


# https://docs.github.com/en/rest/apps/installations?apiVersion=2022-11-28#list-repositories-accessible-to-the-app-installation
request_data = {
    "permission": 'Permissions: None Required',
    "method": "GET",
    "url": f"/installation/repositories",
    "data": None
}

response = make_github_api_request(request_data)
if response.status_code != 200:
    print(response.text)
    raise ValueError(f"Status Code: {response.status_code}")

response_json = response.json()
if len(response_json["repositories"]) == 0:
    raise ValueError("App has access to no repositories")

write_results(results_writer, request_data, response, notes=f"App has access to {str(response_json['total_count'])} repositories")

repository_name = response_json["repositories"][0]["name"]
repository_org = response_json["repositories"][0]["owner"]["login"]

if GH_REPO_NAME and GH_REPO_ORG:
    repository_name = GH_REPO_NAME
    repository_org = GH_REPO_ORG

# ==============================================
# METADATA
# ==============================================

# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
request_data = {
    "permission": 'Permissions: "Metadata" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

repository_description = response.json()["description"] or ""

# ==============================================
# ACTIONS
# ==============================================

# https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository
request_data = {
    "permission": 'Permissions: "Actions" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/actions/runs",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

if str(response.status_code) == "200":
    
    # https://docs.github.com/en/rest/actions/cache?apiVersion=2022-11-28#delete-github-actions-caches-for-a-repository-using-a-cache-key
    request_data = {
        "permission": 'Permissions: "Actions" repository permissions (write)',
        "method": "DELETE",
        "url": f"/repos/{repository_org}/{repository_name}/actions/caches?key=completely_made_up_cache_key_ashjshaudsahds",
        "data": None
    }

    response = make_github_api_request(request_data)
    write_results(results_writer, request_data, response, success_codes=["200", "404"])

# ==============================================
# ADMINISTRATION
# ==============================================

# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-teams
request_data = {
    "permission": 'Permissions: "Administration" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/teams",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

if str(response.status_code) == "200":
    # https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#update-a-repository
    request_data = {
        "permission": 'Permissions: "Administration" repository permissions (write)',
        "method": "PATCH",
        "url": f"/repos/{repository_org}/{repository_name}",
        "data": {"description":repository_description}
    }    
    response = make_github_api_request(request_data)
    write_results(results_writer, request_data, response)



# ==============================================
# CONTENTS
# ==============================================

# https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits
request_data = {
    "permission": 'Permissions: "Contents" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/commits",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

repository_commit_sha = response.json()[0]["sha"]

if str(response.status_code) == "200":
    # https://docs.github.com/en/rest/git/tags?apiVersion=2022-11-28#create-a-tag-object
    request_data = {
        "permission": 'Permissions: "Contents" repository permissions (write)',
        "method": "POST",
        "url": f"/repos/{repository_org}/{repository_name}/git/tags",
        "data": {
            "tag":"tagging_things",
            "message":"initial version",
            "object":"asd",
            "type":"commit",
            "tagger":{"name":"Monalisa Octocat","email":"octocat@github.com","date":"2011-06-17T14:53:35-07:00"}
        }
    }

    response = make_github_api_request(request_data)
    write_results(results_writer, request_data, response, success_codes=["200","422"])    

# ==============================================
# COMMIT STATUSES
# ==============================================

# https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits
request_data = {
    "permission": 'Permissions: "Commit Statuses" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/commits/{repository_commit_sha}/statuses",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

if str(response.status_code) == "200":
    # https://docs.github.com/en/rest/commits/statuses?apiVersion=2022-11-28#create-a-commit-status
    request_data = {
        "permission": 'Permissions: "Commit Statuses" repository permissions (write)',
        "method": "POST",
        "url": f"/repos/{repository_org}/{repository_name}/statuses/{repository_commit_sha}",
        "data": {
            "state":"success",
            "target_url":"https://example.com/build/status",
            "description":"The build succeeded!",
            "context":"continuous-integration/jenkins"
        }
    }

    response = make_github_api_request(request_data)
    write_results(results_writer, request_data, response)

# ==============================================
# DEPLOYMENTS
# ==============================================

# https://docs.github.com/en/rest/deployments/deployments?apiVersion=2022-11-28#list-deployments
request_data = {
    "permission": 'Permissions: "Deployments" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/deployments",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

# ==============================================
# ENVIRONMENTS
# ==============================================

# https://docs.github.com/en/rest/deployments/environments?apiVersion=2022-11-28
request_data = {
    "permission": 'Permissions: "Actions" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/environments",
    "data": None
}

response = make_github_api_request(request_data)

if str(response.status_code) == "200":
    if response.json()["total_count"] > 0:
        environment_name = response.json()["environments"][0]["name"]
        
        # https://docs.github.com/en/rest/actions/variables?apiVersion=2022-11-28#list-environment-variables
        request_data = {
            "permission": 'Permissions: "Environments" repository permissions (read)',
            "method": "GET",
            "url": f"/repos/{repository_org}/{repository_name}/environments/{environment_name}/variables",
            "data": None
        }

        response = make_github_api_request(request_data)
        write_results(results_writer, request_data, response)

        if str(response.status_code) == "200":
            # https://docs.github.com/en/rest/actions/variables?apiVersion=2022-11-28#create-an-environment-variable
            request_data = {
                "permission": 'Permissions: "Environments" repository permissions (write)',
                "method": "POST",
                "url": f"/repos/{repository_org}/{repository_name}/environments/{environment_name}/variables",
                "data": {"name":"test","value":"value"}
            }

            response = make_github_api_request(request_data)
            write_results(results_writer, request_data, response, success_codes=["200", "409"])
    else:
        print("WARNING: Cannot test Environments read permission as no environments")        


# ==============================================
# ISSUES
# ==============================================

# https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#list-repository-issues
request_data = {
    "permission": 'Permissions: "Issues" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/issues",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)


# ==============================================
# PULL REQUESTS
# ==============================================

# https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests
request_data = {
    "permission": 'Permissions: "Pull Requests" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/pulls?state=all",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

if str(response.status_code) == "200":
    if len(response.json()) > 0:
        pull_request_number = response.json()[0]["number"]
        pull_request_title = response.json()[0]["title"]

        # https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#update-a-pull-request
        request_data = {
            "permission": 'Permissions: "Pull Requests" repository permissions (write)',
            "method": "PATCH",
            "url": f"/repos/{repository_org}/{repository_name}/pulls/{pull_request_number}",
            "data": {"title":pull_request_title}
        }

        response = make_github_api_request(request_data)
        write_results(results_writer, request_data, response)
    else:
        print("WARNING: Cannot test Pull Request write permission as no PRs")


# ==============================================
# WEBHOOKS
# ==============================================

# https://docs.github.com/en/rest/repos/webhooks?apiVersion=2022-11-28#list-repository-webhooks
request_data = {
    "permission": 'Permissions: "Webhooks" repository permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/{repository_name}/hooks",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

if str(response.status_code) == "200":
    request_data = {
        "permission": 'Permissions: "Webhooks" repository permissions (write)',
        "method": "POST",
        "url": f"/repos/{repository_org}/{repository_name}/hooks",
        "data": {
            "name":"web",
            "active":False,
            "events":["push","pull_request"],
            "config":{"url":"https://thomaspreece.com/webhook","content_type":"json","insecure_ssl":"0"}
        }
    }

    response = make_github_api_request(request_data)
    write_results(results_writer, request_data, response)

    webhook_id = response.json()["id"]

    request_data = {
        "permission": 'Permissions: "Webhooks" repository permissions (write)',
        "method": "DELETE",
        "url": f"/repos/{repository_org}/{repository_name}/hooks/{webhook_id}",
        "data": None
    }

    response = make_github_api_request(request_data)


# ================= ORGANISATION PERMISSIONS ================================

# ==============================================
# MEMBERS
# ==============================================

# https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28#list-organization-members
request_data = {
    "permission": 'Permissions: "Members" organisation permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/members",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)


# ==============================================
# WEBHOOKS
# ==============================================

# https://docs.github.com/en/rest/orgs/webhooks?apiVersion=2022-11-28#list-organization-webhooks
request_data = {
    "permission": 'Permissions: "Webhooks" organisation permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/hooks",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

if str(response.status_code) == "200":
    # https://docs.github.com/en/rest/orgs/webhooks?apiVersion=2022-11-28#create-an-organization-webhook
    request_data = {
        "permission": 'Permissions: "Webhooks" organisation permissions (write)',
        "method": "POST",
        "url": f"/repos/{repository_org}/hooks",
        "data": {
            "name":"web",
            "active":False,
            "events":["push","pull_request"],
            "config":{"url":"https://thomaspreece.com/webhook","content_type":"json","insecure_ssl":"0"}
        }
    }

    response = make_github_api_request(request_data)
    write_results(results_writer, request_data, response)

    webhook_id = response.json()["id"]

    request_data = {
        "permission": 'Permissions: "Webhooks" organisation permissions (write)',
        "method": "DELETE",
        "url": f"/repos/{repository_org}/hooks/{webhook_id}",
        "data": None
    }

    response = make_github_api_request(request_data)


# ==============================================
# SELF-HOSTED RUNNERS
# ==============================================

# https://docs.github.com/en/rest/actions/self-hosted-runners?apiVersion=2022-11-28#list-self-hosted-runners-for-an-organization
request_data = {
    "permission": 'Permissions: "Self Hosted Runners" organisation permissions (read)',
    "method": "GET",
    "url": f"/repos/{repository_org}/actions/runners",
    "data": None
}

response = make_github_api_request(request_data)
write_results(results_writer, request_data, response)

if str(response.status_code) == "200":
    # https://docs.github.com/en/rest/orgs/webhooks?apiVersion=2022-11-28#create-an-organization-webhook
    request_data = {
        "permission": 'Permissions: "Self Hosted Runners" organisation permissions (write)',
        "method": "POST",
        "url": f"/repos/{repository_org}/actions/runners/registration-token",
        "data": None
    }

    response = make_github_api_request(request_data)
    write_results(results_writer, request_data, response)
