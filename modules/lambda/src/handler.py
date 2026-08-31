import json
import logging
import os
import re

import boto3


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ============================================================
# AWS CLIENTS
# ============================================================

bedrock = boto3.client("bedrock-runtime")
cloudwatch = boto3.client("cloudwatch")


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "ca.amazon.nova-lite-v1:0"
)

METRIC_NAMESPACE = "NextGen-AI-Security"


# ============================================================
# PROMPT INJECTION DETECTION
# ============================================================

def detect_prompt_injection(prompt):
    """
    Detect common prompt-injection patterns.

    WHAT:
    Looks for instructions attempting to override system
    or security instructions.

    WHY:
    Prompt injection is one of the primary threats to
    applications that expose LLMs to user-controlled input.
    """

    patterns = [
        r"ignore previous instructions",
        r"ignore all previous instructions",
        r"disregard previous instructions",
        r"disregard all previous instructions",
        r"forget previous instructions",
        r"override previous instructions",
        r"reveal your system prompt",
        r"show me your system prompt",
        r"print your system prompt",
        r"reveal hidden instructions",
        r"ignore your instructions",
        r"bypass your instructions"
    ]

    prompt_lower = prompt.lower()

    for pattern in patterns:
        if re.search(pattern, prompt_lower):
            return True

    return False


# ============================================================
# DLP / SENSITIVE DATA DETECTION
# ============================================================

def contains_sensitive_data(text):
    """
    Detect potentially sensitive information.

    WHAT:
    Looks for common credential and secret patterns.

    WHY:
    Prevents users from sending secrets to the AI model
    and also prevents the model from accidentally returning
    sensitive information.
    """

    patterns = [
        r"password\s*[:=]",
        r"passwd\s*[:=]",
        r"secret\s*[:=]",
        r"api[_-]?key\s*[:=]",
        r"access[_-]?key\s*[:=]",
        r"private[_-]?key\s*[:=]",
        r"token\s*[:=]",
        r"authorization\s*[:=]",
        r"bearer\s+[A-Za-z0-9\-_\.]+"
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


# ============================================================
# CLOUDWATCH SECURITY LOGGING
# ============================================================

def log_security_event(request_id, control, action, reason):
    """
    Write a structured security event to CloudWatch Logs.
    """

    logger.info(
        json.dumps(
            {
                "event": "security_event",
                "request_id": request_id,
                "control": control,
                "action": action,
                "reason": reason,
                "model": MODEL_ID
            }
        )
    )


# ============================================================
# CLOUDWATCH SECURITY METRICS
# ============================================================

def publish_security_metric(control, action):
    """
    Publish a custom CloudWatch security metric.

    WHAT:
    Creates a metric for ALLOW or BLOCK security events.

    WHY:
    Metrics make it easier to build dashboards, alarms,
    and security KPIs.
    """

    cloudwatch.put_metric_data(
        Namespace=METRIC_NAMESPACE,
        MetricData=[
            {
                "MetricName": "SecurityEvents",
                "Dimensions": [
                    {
                        "Name": "Control",
                        "Value": control
                    },
                    {
                        "Name": "Action",
                        "Value": action
                    }
                ],
                "Value": 1,
                "Unit": "Count"
            }
        ]
    )


# ============================================================
# BEDROCK MODEL INVOCATION
# ============================================================

def invoke_model(prompt):
    """
    Send the approved prompt to Amazon Bedrock.

    WHAT:
    Calls the configured Amazon Nova model.

    WHY:
    This function is only called after the prompt passes
    our gateway security controls.
    """

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    )

    return response["output"]["message"]["content"][0]["text"]


# ============================================================
# AI OUTPUT SECURITY INSPECTION
# ============================================================

def inspect_model_output(text):
    """
    Inspect the AI model response before returning it.

    WHAT:
    Checks model output for potentially sensitive information.

    WHY:
    AI security must protect both sides of the interaction:

        User -> AI
        AI -> User

    The model should not accidentally return credentials,
    tokens, passwords, private keys, or other sensitive data.

    RETURNS:
        True  = sensitive information detected
        False = output appears safe
    """

    if not text:
        return False

    if contains_sensitive_data(text):
        return True

    return False


# ============================================================
# LAMBDA HANDLER
# ============================================================

def handler(event, context):
    """
    Main AI security gateway.

    Security flow:

        1. Receive request
        2. Extract prompt
        3. DLP inspection
        4. Prompt-injection inspection
        5. Log ALLOW/BLOCK decision
        6. Invoke Bedrock
        7. Inspect AI output
        8. Return safe response
    """

    request_id = context.aws_request_id

    # ========================================================
    # REQUEST PARSING
    # ========================================================

    try:
        body = event.get("body", {})

        if isinstance(body, str):
            body = json.loads(body)

        prompt = body.get("prompt", "").strip()

    except Exception:

        logger.warning(
            json.dumps(
                {
                    "event": "invalid_request",
                    "request_id": request_id
                }
            )
        )

        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "error": "Invalid request body",
                    "request_id": request_id
                }
            )
        }

    # ========================================================
    # VALIDATE PROMPT
    # ========================================================

    if not prompt:

        logger.warning(
            json.dumps(
                {
                    "event": "invalid_request",
                    "request_id": request_id,
                    "reason": "missing_prompt"
                }
            )
        )

        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "error": "Prompt is required",
                    "request_id": request_id
                }
            )
        }

    # ========================================================
    # DLP SECURITY CONTROL
    # ========================================================

    if contains_sensitive_data(prompt):

        log_security_event(
            request_id=request_id,
            control="dlp",
            action="BLOCK",
            reason="potential_secret_detected"
        )

        publish_security_metric(
            control="dlp",
            action="BLOCK"
        )

        logger.warning(
            json.dumps(
                {
                    "event": "dlp_blocked_request",
                    "request_id": request_id,
                    "reason": "potential_secret_detected"
                }
            )
        )

        return {
            "statusCode": 403,
            "body": json.dumps(
                {
                    "error": "Request blocked by AI security policy",
                    "request_id": request_id
                }
            )
        }

    # ========================================================
    # PROMPT INJECTION SECURITY CONTROL
    # ========================================================

    if detect_prompt_injection(prompt):

        log_security_event(
            request_id=request_id,
            control="prompt_injection",
            action="BLOCK",
            reason="potential_prompt_injection_detected"
        )

        publish_security_metric(
            control="prompt_injection",
            action="BLOCK"
        )

        logger.warning(
            json.dumps(
                {
                    "event": "prompt_injection_blocked",
                    "request_id": request_id,
                    "reason": "potential_prompt_injection_detected"
                }
            )
        )

        return {
            "statusCode": 403,
            "body": json.dumps(
                {
                    "error": "Request blocked by AI security policy",
                    "request_id": request_id
                }
            )
        }

    # ========================================================
    # REQUEST PASSED SECURITY CONTROLS
    # ========================================================

    log_security_event(
        request_id=request_id,
        control="gateway",
        action="ALLOW",
        reason="request_passed_security_controls"
    )

    publish_security_metric(
        control="gateway",
        action="ALLOW"
    )

    # ========================================================
    # INVOKE AMAZON BEDROCK
    # ========================================================

    try:

        model_response = invoke_model(prompt)

    except Exception as error:

        logger.error(
            json.dumps(
                {
                    "event": "model_invocation_error",
                    "request_id": request_id,
                    "error": str(error)
                }
            )
        )

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": "AI model invocation failed",
                    "request_id": request_id
                }
            )
        }

    # ========================================================
    # AI OUTPUT SECURITY CONTROL
    # ========================================================

    if inspect_model_output(model_response):

        log_security_event(
            request_id=request_id,
            control="output_security",
            action="BLOCK",
            reason="sensitive_data_detected_in_model_output"
        )

        publish_security_metric(
            control="output_security",
            action="BLOCK"
        )

        logger.warning(
            json.dumps(
                {
                    "event": "ai_output_blocked",
                    "request_id": request_id,
                    "reason": "sensitive_data_detected_in_model_output"
                }
            )
        )

        return {
            "statusCode": 403,
            "body": json.dumps(
                {
                    "error": "AI response blocked by security policy",
                    "request_id": request_id
                }
            )
        }

    # ========================================================
    # SUCCESSFUL AI RESPONSE
    # ========================================================

    logger.info(
        json.dumps(
            {
                "event": "ai_request_completed",
                "request_id": request_id,
                "control": "output_security",
                "action": "ALLOW"
            }
        )
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(
            {
                "model": MODEL_ID,
                "response": model_response,
                "request_id": request_id
            }
        )
    }