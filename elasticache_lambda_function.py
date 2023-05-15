import os
import boto3
import requests

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']


def send_slack_notification(message):
    payload = {
        'channel': '#alerts',
        'text': message
    }
    requests.post(SLACK_WEBHOOK_URL,
                  json=payload)


def lambda_handler(event, context):
    elasticache = boto3.client('elasticache')
    response = elasticache.describe_update_actions()
    message = ""

    updates_not_applied = []
    for update_action in response['UpdateActions']:
        if update_action['UpdateActionStatus'] == 'not-applied':
            updates_not_applied.append(update_action)

    if updates_not_applied:
        message = f"ElastiCache updates not applied: {len(updates_not_applied)}\n"
        for update in updates_not_applied:
            message += f"Cluster Name: {update['ReplicationGroupId']}, Severity: {update['ServiceUpdateSeverity']},\n" \
                       f"Release Date: {update['ServiceUpdateReleaseDate']}, \n" \
                       f"Service Update Name: {update['ServiceUpdateName']}, \n" \
                       f"Service Update Type: {update['ServiceUpdateType']} \n"

        send_slack_notification(message)
    else:
        message = "No ElastiCache updates at this moment."

    return message
