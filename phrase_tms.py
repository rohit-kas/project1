import requests
import time
import random
from github import Github



def get_auth_token():
    url = "https://cloud.memsource.com/web/api2/v1/auth/login"
    headers = {'content': 'application/json'}
    body ={ "userName":"phrase.admin",
            "password":"AdminPhrase#20231"
        
        }

    respose = requests.post(url=url,headers=headers,json=body)
    data = respose.json()
    auth_token = data['token']
    return auth_token
#####====================== Create Project =================================

def create_project(auth_token,body_content):
    project_id = project_list(auth_token,body_content[0])
    if project_id :
        return project_id
    else:
        body = { 
                        "name":body_content[0],
                        "sourceLang":body_content[1],
                        "targetLangs":body_content[2]
                        }
        headers = { 'content': 'application/json',
                    'Authorization':f'ApiToken {auth_token}'
                    }
        url = "https://cloud.memsource.com/web/api2/v1/projects"
        respose = requests.post(url=url,headers=headers,json=body)
        data = respose.json()
        return data['uid']

def project_list(auth_token,project_name):
    headers = { 'content': 'application/json',
                'Authorization':f'ApiToken {auth_token}'
                }
    url = "https://cloud.memsource.com/web/api2/v1/projects"
    response = requests.get(url=url,headers=headers)
    projects = response.json()
    projects = projects['content']
    project_id = None
    for project in projects:
        if project['name'] == project_name:
            project_id = project['uid']
    return project_id

#####====================== Create User =================================

def create_user(auth_token,first_name,last_name,email):
    i = random.randint(1,10000)
    user_name = first_name+last_name+"-"+f"{i}"
    body = {
            "userName": user_name,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "password": "Test@1234567",
            "role": "LINGUIST",
            "timezone": "Europe/London",
            "receiveNewsletter": True,
            "note": "string",
            "active": True
            }
    headers = { 'content': 'application/json',
                'Authorization':f'ApiToken {auth_token}'
                }
    url = "https://cloud.memsource.com/web/api2/v3/users"
    respose = requests.post(url=url,headers=headers,json=body)
    data = respose.json()
    time.sleep(2)
    url = "https://cloud.memsource.com/web/api2/v1/users"
    respose = requests.get(url=url,headers=headers)
    users = respose.json()
    users = users['content']
    for user in users:
        if user['userName'] == user_name:
            user_id = user['id']
            return user_id,user['userName']

#####========================= Create Vendor ====================================

def create_vendor(vendor_token):
    url = "https://cloud.memsource.com/web/api2/v1/vendors"
    body = {
            "vendorToken" : vendor_token
            }

#####====================== Create Jobs and Assign =================================

def create_job(auth_token,trgt_lang,user_id,project_id): #,file_suffix,src_lang
    headers = { 'Content-Type': 'application/octet-stream',
                'Authorization':f'ApiToken {auth_token}',
                'Memsource' : '{"targetLangs": [  "'+ trgt_lang +'"  ],"due": "2023-12-03T10:15:30.00Z","assignments": [ { "targetLang": "'+ trgt_lang +'",   "providers": [ {"id": "'+ user_id +'","type": "USER" } ] } ], "notifyProvider": { "organizationEmailTemplate": { "id": "1"  },  "notificationIntervalInMinutes": "10"  }}',
                'Content-Disposition' : 'attachment; filename="en.yml"'
                }
    
    url = f"https://cloud.memsource.com/web/api2/v1/projects/{project_id}/jobs"
    file_path = '/home/hp/Desktop/en.yml'

    with open(file_path, "rb") as f:
        binary_data = f.read()
    utf_data = binary_data.decode("utf-8")
    response = requests.post(url, headers=headers,data=utf_data)
    result = response.json()
    job_id = result['jobs'][0]['uid']
    return job_id

#####====================== Export File From Phrase to Github ===================

def export_file(auth_token,project_id,job_id):
    headers = { 'content': 'application/json',
                'Authorization':f'ApiToken {auth_token}'
                }
    body = {
            "jobs": [
                    { "uid": job_id }
                    ]
            }
    time.sleep(2)
    url = f"https://cloud.memsource.com/web/api2/v3/projects/{project_id}/jobs/export"
    response = requests.post(url=url,headers=headers,json=body)
    jobs = response.json()
    print("file exported to github successfully....!!")
    return job_id

####================================== Update Jobs ==============================

def update_job(auth_token,project_id,job_id,file=""):
    headers = { 'Content-Type': 'application/octet-stream',
                'Authorization':f'ApiToken {auth_token}',
                'Memsource' : '{  "jobs": [   {     "uid":' + job_id +'    }  ],  "preTranslate": False,  "allowAutomaticPostAnalysis": False,  "callbackUrl": "https://webhook.site/4ea46614-4108-4207-871e-5685d8c9c4a4"}',
                'Content-Disposition' : 'attachment; filename="en.yml"'
                }

    url = f"https://cloud.memsource.com/web/api2/v1/projects/{project_id}/jobs/source"
    file_path = '/home/hp/Desktop/en.yml'

    with open(file_path, "rb") as f:
        binary_data = f.read()
    utf_data = binary_data.decode("utf-8")
    response = requests.post(url, headers=headers,data=binary_data)
    result = response.json()

####================================= Download file from github =================
def get_github_file():
    
    github = Github('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')
    user = github.get_user()
    repository = user.get_repo('phrase-demo')
    file_content = repository.get_contents('en/en.yml',ref="master")
    r = file_content.decoded_content.decode()
    file_path = '/home/hp/Desktop/en.yml'
    with open(file_path, 'w') as f:
        f.write(r)
    print("File downloaded successfully....!!!!!")


####========================== Download translated file in local ========================

def download_translated_file(auth_token,project_id,job_id,file_name):
    headers = { 'content': 'application/json',
                'Authorization':f'ApiToken {auth_token}'
                }
  
    url = f"https://cloud.memsource.com/web/api2/v2/projects/{project_id}/jobs/{job_id}/targetFile"
    response = requests.put(url=url,headers=headers)
    data = response.json()
    asyncRequestId = data['asyncRequest']['id']
    time.sleep(2)
    url = f"https://cloud.memsource.com/web/api2/v2/projects/{project_id}/jobs/{job_id}/downloadTargetFile/{asyncRequestId}"
    response = requests.get(url=url,headers=headers)
    file_path = file_name
    with open(file_path, "wb") as f:
        f.write(response.content)
    
    print("File Downloaded")

####========================== Push file to github =========================================

def push_to_github(GIT_ACCESS_TOKEN,REPO_NAME,GIT_FOLDER_NAME,FILE_NAME,BRANCH):
    g = Github(GIT_ACCESS_TOKEN)
    repo = g.get_user().get_repo(REPO_NAME)
    all_files = []
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

    with open(FILE_NAME, 'r') as file:
        content = file.read()

    # Upload to github
    git_prefix = GIT_FOLDER_NAME
    git_file = git_prefix + FILE_NAME
    if git_file in all_files:
        contents = repo.get_contents(git_file)
        repo.update_file(contents.path, "committing files", content, contents.sha, branch=BRANCH)
        print(git_file + ' Pushed into Repository!!!! (Updated)')
    else:
        repo.create_file(git_file, "committing files", content, branch=BRANCH)
        print(git_file + ' Pushed into Repository!!!!')

####================================== List of Jobs =========================================

def job_list(auth_token,project_id):
    headers = { 'content': 'application/json',
                'Authorization':f'ApiToken {auth_token}'
                }
    url = f"https://cloud.memsource.com/web/api2/v2/projects/{project_id}/jobs"
    response = requests.get(url=url,headers=headers)
    result = response.json()
    jobs = result['content']
    # job_list = []
    return jobs
        
