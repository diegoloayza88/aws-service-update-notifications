import boto3
import os
import requests
import json

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']


def send_slack_notification(message):
    payload = {
        'channel': '#alerts',
        'text': message
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)

    if response.status_code != 200:
        raise Exception('Failed to send Slack alert')


def lambda_handler(event, context):
    rds = boto3.client('rds')
    message = ""

    pending_actions = rds.describe_pending_maintenance_actions()

    for pending_action in pending_actions['PendingMaintenanceActions']:
        if pending_action:
            resource_identifier = pending_action['ResourceIdentifier']
            for pending_action_details in pending_action['PendingMaintenanceActionDetails']:
                if pending_action_details:
                    if 'CurrentApplyDate' in pending_action_details:
                        message = f"No pending RDS maintenance actions at this moment in: `{resource_identifier}` \n"
                    else:
                        message = f"Pending maintenance actions for RDS instances `{resource_identifier}`: \n" \
                                  f"Action: {pending_action_details['Action']}, \n" \
                                  f"Description: {pending_action_details['Description']} \n"
                        if 'OptInStatus' in pending_action_details:
                            message += f"OptInStatus: {pending_action_details['OptInStatus']} \n"
                        send_slack_notification(message)
        else:
            message = "No existing information regarding pending maintenance action on RDS."

    return message
