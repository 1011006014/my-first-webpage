import json
import os
import sys

import boto3
from moto import mock_aws

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ["TABLE_NAME"] = "test-visitor-count"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lambda"))


@mock_aws
def test_count_increments():
    boto3.client("dynamodb").create_table(
        TableName="test-visitor-count",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    import importlib
    import visitor_counter
    importlib.reload(visitor_counter)

    first = visitor_counter.lambda_handler({}, None)
    second = visitor_counter.lambda_handler({}, None)

    assert first["statusCode"] == 200
    assert json.loads(first["body"])["count"] == 1
    assert json.loads(second["body"])["count"] == 2
