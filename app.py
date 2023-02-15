from flask import Flask, request
from phrase_TMS import get_auth_token,get_github_file,create_project,create_user,create_job,create_vendor,update_job,download_translated_file,push_to_github,job_list
import time

INITIALIZE = True


app = Flask(__name__)

@app.route('/output', methods=['GET','POST'])
def output():
    global INITIALIZE
    if INITIALIZE :
        print("initialize begin for phrase TMS ")
        get_github_file() #1
        auth_token = get_auth_token() #2
        project_details = ['SampleProject1',"en",[ "de","fr" ]]
        project_id = create_project(auth_token,project_details) #3
        print("Project Created...!!!!!")
        first_name = 'Atul'
        last_name = 'Asati'
        emails = ['phrasedmn@gmail.com','phrasevend@gmail.com']
        trgt_lang = 'fr'
        for email in emails:
            user_id,user_name = create_user(auth_token,first_name,last_name,email) #4
            job_id = create_job(auth_token,trgt_lang,user_id,project_id) #5
            print("Job created for user with user Name :",user_name)
        INITIALIZE = False
        return 'Initialize Success'
    else :
        data = request.get_json()
        print(data)
        get_github_file()
        auth_token = get_auth_token() #2
        project_details = ['SampleProject1',"en",[ "de","fr" ]]
        project_id = create_project(auth_token,project_details) #3
        jobs = job_list(auth_token,project_id)
        for job in jobs:
            job_id = job['uid']
            job_status = job['status']
            job_assigned_user = job['providers'][0]['uid']
            user_name = job['providers'][0]['userName']
            if job_status != 'COMPLETED':
                update_job(auth_token,project_id,job_id)
                print("job Updated for user_name : ",user_name)
        # print(data)
        return 'Update Job Success'


@app.route('/completion', methods=['POST'])
def completion():
    data = request.get_json()
    # print(data)
    status = data['jobParts'][0]['status']
    print(status)
    if status == 'COMPLETED_BY_LINGUIST':
        auth_token = get_auth_token()
        # print("auth_token",auth_token)
        project_id = data['jobParts'][0]['project']['uid']
        # print("project_id",project_id)
        job_id = data['jobParts'][0]['uid']
        # print("job_id",job_id)
        trgt_lang = data['jobParts'][0]['targetLang']
        file_name = "completed_"+data['jobParts'][0]['fileName']
        print("file name :",file_name)
        folder_name = f"{trgt_lang}/"
        repo_name = f"phrase-{trgt_lang}"
        print(f"Pushing the translated file {file_name} in github repo {repo_name}")
        download_translated_file(auth_token,project_id,job_id,file_name)
        time.sleep(5)
        push_to_github(GIT_ACCESS_TOKEN="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",REPO_NAME=repo_name,GIT_FOLDER_NAME=folder_name,FILE_NAME=file_name,BRANCH="master")

    return 'Success'

if __name__ == '__main__':
    app.run(Debug=True)
