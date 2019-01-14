from os import walk
import os
import boto3
import time


def importCSVtoDynamoDB(table_name):
   
    print('- Step 1: Connecting to DynamoDB...')
    dynamodb_conn = boto3.resource('dynamodb')
    print('- Step 2: Accessing table ' + table_name)
    dynamodb_table = dynamodb_conn.Table(table_name)

    print('- Step 3: Opening ' + table_name + '.csv')
    csv_file = open('csv/to_import/' + table_name + '.csv', 'r')
    header = csv_file.readline().strip().split(',')
    print('- Step 4: Got table headers :', header)

    for line in csv_file:
        line = line.strip().split(',')

        row = {}
        for colunm_number, colunm_name in enumerate(header):
            row[colunm_name] = str(line[colunm_number])
        
        print('--- INFO: Importing row: ', row)
        dynamodb_table.put_item(Item=row)

    print('- Step 5: Closing csv file...')
    csv_file.close() 
   

def importFiles():

    for (dirpath, dirnames, filenames) in walk('csv/to_import/'):
        for i in range(0,len(filenames)):
            csv_file = filenames[i][0:len(filenames[i])-4]
            print('--- INFO: Starting import for ' + csv_file)
            start_time = time.time()
            importCSVtoDynamoDB(csv_file)
            end_time = time.time()
            import_time_information = "(import time: " + \
                                        str(round(end_time - start_time, 3)) + ")"
            print('--- INFO: End of import. Enjoy !', import_time_information, '\n')
        break

if __name__ == "__main__":

    if os.path.isfile('csv/to_import/awscert_user_t.csv'):
        print('--- WARNING: it seems you have transformed a file and have duplicated awscert_user tables.' \
        + '\n' + 'Please choose file you want to use and rename it into "awscert_user.csv" before.')
    else:
        importFiles()