import boto3
import os
import time
from slacker import Slacker
from utils.configuration import Configuration

def getUDIDforEmails():

    slack_token = Configuration().slack_token
    print('--- INFO: Connect to Slack')
    slack = Slacker(slack_token)

    udids_and_emails = {}
    print('--- INFO: Call Slack API to list Users')
    response = slack.users.list()
    users = response.body['members']

    for user in users:
        if not user['deleted']:
            try:
                email = user['profile']['email']
            except KeyError:
                email = "no@adress.com"
            udids_and_emails[email]=user['id']

    return udids_and_emails

def transformEmailsIntoUsers(csv_filename):

    start_time = time.time()
    print('- Step 1: List Slack users and get emails')
    udids_and_emails = getUDIDforEmails()

    print('- Step 2: Create new file' + csv_filename + '.csv in "csv/to_import/"')
    transformed_csv = open('csv/to_import/' + csv_filename + '.csv',"w+")
    transformed_csv.write('user_id,certification_level' + '\n')

    print('- Step 3: Open file user_email.csv to transform')
    csv_to_transform = open('csv/to_transform/user_email.csv', 'r')
    csv_to_transform.readline().strip().split(',')

    print('- Step 4: Fill in awscert_user_t.csv with user_id and certification_level')
    for line in csv_to_transform:
        line = line.strip().split(',')
        try:
            udid = udids_and_emails[line[0]]
        except:
            udid = "nothing"
        transformed_csv.write(udid + ',' + str(line[1]) + '\n')

    end_time = time.time()
    transform_time_information = "(transform time: " + \
                                    str(round(end_time - start_time, 3)) + ")"
    print('- END OF JOB: You now have a new file in "csv/to_import" that can safely be imported. Enjoy !', \
            transform_time_information, '\n')
    csv_to_transform.close()
    transformed_csv.close()

if __name__ == "__main__":

    if os.path.isfile('csv/to_import/awscert_user.csv'):
        print('--- WARNING: awscert_user already exists, will create new file awscert_user_t.csv')
        transformEmailsIntoUsers('awscert_user_t')
    else:
        transformEmailsIntoUsers('awscert_user')

