# everyoneoutofthepool
Programmatically revoke active sessions for assumed AWS roles 

This tool replicates the process carried out by executing 'Revoke active sessions' in the IAM dashboard of the AWS management console, as discussed here:
https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html

In its current state, the tool will try to do this for all modifiable roles in the default account, as specified in the local AWS credentials file.
