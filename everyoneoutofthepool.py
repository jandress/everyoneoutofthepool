#!/usr/bin/python

import boto3
import json
import datetime

#get the AWS policy info from the specified file
def get_policy_body(data_file):
    print("in get_policy_body")
    print("data_file is "+data_file)
    with open(data_file) as data_file:
        data = data_file.read()
    return data

#update the AWS role with the policy
def update_role(role_name, client,iam_policy_name,policy_document):
    print("in update_role ")
    print("role name is "+role_name)
    response = client.put_role_policy(
    RoleName=role_name,
    PolicyName=iam_policy_name,
    PolicyDocument=policy_document
    )

    print ("Response from AWS is:")
    print(response)

#list out the roles in the account
def get_roles(client):
    print("in get_roles")
    client = boto3.client('iam')
    response = None
    role_names = []
    marker = None

    # By default, only 100 roles are returned at a time.
    # 'Marker' is used for pagination.
    while (response is None or response['IsTruncated']):
        # Marker is only accepted if result was truncated.
        if marker is None:
            response = client.list_roles()
        else:
            response = client.list_roles(Marker=marker)

        roles = response['Roles']
        for role in roles:
            #print(role['Arn'])
            role_names.append(role['RoleName'])

        if response['IsTruncated']:
            marker = response['Marker']

    return role_names

#update the timestamp in the policy file to now(ish)
def fix_token_timestamp(policy_file):
    print("in fix_token_timestamp")
    print("policy file is "+policy_file)
    timestamp_now = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')
    print("updating policy TokenIssueTime to"+timestamp_now)

    jsonFile = open(policy_file, "r")
    data = json.load(jsonFile)
    jsonFile.close()

    data['Statement'][0]['Condition']['DateLessThan']['aws:TokenIssueTime'] = timestamp_now

    jsonFile = open(policy_file, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

def main():
    print("in main")
    ##this should be modified to match the seciton name in your AWS credentials file
    #or look at the code here \/ to see how to loop through all the credential sections
    #https://github.com/jandress/sg_audit/blob/master/sg_audit.py
    boto3.Session(profile_name = "default")
    client = boto3.client('iam')

    #info for the policy that we'll be attaching
    policy_file = "AWSRevokeOlderSessions.json"
    policy_name = "AWSRevokeOlderSessions"
    print("policy file is "+policy_file)

    #update the timestamp in the policy file
    fix_token_timestamp(policy_file)

    policy_document = get_policy_body(policy_file)

    roles = get_roles(client)

    #loop through all the roles and attach the policy to them
    for role in roles:
        print("found role "+role)
        if "AWSServiceRole" in role:
            print ("skipping "+role+" this is an unmodifyable AWS role") #modifying the AWSServiceRoles is verboten
        else:
            update_role(role,client,policy_name,policy_document)
    print("exiting")

if __name__ == "__main__":
    main()
