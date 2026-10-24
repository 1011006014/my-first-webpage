import json
import os

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "visitor-count")
COUNTER_ID = "resume"

table = boto3.resource("dynamodb").Table(TABLE_NAME)


def lambda_handler(event, context):
    # ADD is atomic, so concurrent visitors never overwrite each other,
    # and it creates the item on the first visit.
    result = table.update_item(
        Key={"id": COUNTER_ID},
        UpdateExpression="ADD visits :one",
        ExpressionAttributeValues={":one": 1},
        ReturnValues="UPDATED_NEW",
    )
    count = int(result["Attributes"]["visits"])
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"count": count}),
    }
