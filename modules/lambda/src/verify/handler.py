import json
import logging
import os
import re
import uuid

import boto3


# =========================================================
# LOGGING CONFIGURATION
# =========================================================
#
# PURPOSE:
# Configure Python logging so Lambda can send application
# and security events to Amazon CloudWatch Logs.
#
# WHY:
# Security teams need an audit trail showing what happened
# during every AI request.
# =========================================================

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# =========================================================
# AWS CLIENTS
# =========================================================
#
# PURPOSE:
# Create clients that allow this Lambda function to
# communicate with AWS services.
#
# WHY:
# The AI agent needs:
#   1. Bedrock     -> to communicate with the AI model
#   2. CloudWatch  -> to publish security metrics
#
# The Lambda execution role determines what actions
# these clients are allowed to perform.
# =========================================================

bedrock = boto3.client("bedrock-runtime")

cloudwatch = boto3.client("cloudwatch")


# =========================================================
# MODEL CONFIGURATION
# =========================================================
#
# PURPOSE:
# Read the Bedrock model ID from an environment variable.
#
# WHY:
# Keeping configuration outside the code makes the
# application easier to change between environments.
#
# Terraform currently provides:
#
#   BEDROCK_MODEL_ID
#
# If the variable does not exist, we use Nova Lite as
# the default model.
# =========================================================

MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "ca.amazon.nova-lite-v1:0"
)


# =========================================================
# SECURITY AUDIT LOGGING
# =========================================================
#
# PURPOSE:
# Write standardized security events to CloudWatch Logs.
#
# WHY:
# A security gateway needs an audit trail.
#
# Example event:
#
# {
#   "event": "security_event",
#   "control": "dlp",
#   "action": "BLOCK"
# }
#
# These events can later be searched, analyzed, and
# displayed on our CloudWatch security dashboard.
# =========================================================

def log_security_event(
    request_id,
    control,
    action,
    reason
):
    """
    Write a standardized security audit event.

    request_id:
        Unique identifier for the request.

    control:
        Security control that handled the request.

    action:
        Result of the security control.
        Example: ALLOW or BLOCK.

    reason:
        Explanation for the security decision.
    """

    logger.info(
        json.dumps({
            "event": "security_event",
            "request_id": request_id,
            "control": control,
            "action": action,
            "reason": reason,
            "model": MODEL_ID
        })
    )


# =========================================================
# CLOUDWATCH SECURITY METRICS
# =========================================================
#
# PURPOSE:
# Publish numerical security metrics to CloudWatch.
#
# WHY:
# Logs tell us detailed information about an event.
#
# Metrics allow CloudWatch to COUNT events and create:
#
#   - Dashboards
#   - Alarms
#   - Monitoring graphs
#   - Security KPIs
#
# Namespace:
#
#   NextGen/AISecurity
#
# Example metrics:
#
#   AllowedRequests
#   DLPBlockedRequests
#   PromptInjectionBlockedRequests
#
# Each security event increases its corresponding metric
# by 1.
# =========================================================

def publish_security_metric(metric_name):
    """
    Publish a single security event to CloudWatch.

    metric_name:
        Name of the security metric to increment.
    """

    cloudwatch.put_metric_data(
        Namespace="NextGen/AISecurity",
        MetricData=[
            {
                "MetricName": metric_name,

                # Add one event to the metric.
                "Value": 1,

                # The metric represents a count of events.
                "Unit": "Count"
            }
        ]
    )


# =========================================================
# DLP SECURITY CONTROL
# =========================================================
#
# PURPOSE:
# Detect potential sensitive credentials and secrets
# before the request reaches the AI model.
#
# WHY:
# Sensitive information should not be unnecessarily sent
# to an AI model.
#
# This provides a basic Data Loss Prevention (DLP) layer.
# =========================================================

def contains_sensitive_data(text):
    """
    Detect common sensitive credential patterns.

    Detects:
        - AWS Access Key IDs
        - Obfuscated AWS Access Key IDs
        - Generic secrets/passwords/API keys
        - Private keys
        - JWT tokens
    """

    if not text:
        return False

    # -----------------------------------------------------
    # NORMALIZE OBFUSCATED INPUT
    # -----------------------------------------------------
    #
    # Attackers may try to bypass simple pattern matching
    # by inserting spaces or hyphens.
    #
    # Example:
    #
    #   A K I A 123456...
    #
    # becomes:
    #
    #   AKIA123456...
    #
    # This allows the security control to detect
    # simple obfuscation attempts.

    normalized = re.sub(r"[\s\-]", "", text)


    # -----------------------------------------------------
    # SENSITIVE DATA PATTERNS
    # -----------------------------------------------------

    patterns = [

        # AWS Access Key IDs
        r"\bAKIA[0-9A-Z]{16}\b",

        # AWS temporary access key IDs
        r"\bASIA[0-9A-Z]{16}\b",

        # Generic secret/key assignments
        r"(?i)\b(secret|password|passwd|api[_-]?key|access[_-]?key)\s*[:=]\s*[^\s]+",

        # Private keys
        r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",

        # JWT tokens
        r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b",
    ]


    # -----------------------------------------------------
    # CHECK ORIGINAL TEXT
    # -----------------------------------------------------

    for pattern in patterns:

        if re.search(pattern, text):
            return True


    # -----------------------------------------------------
    # CHECK OBFUSCATED AWS CREDENTIALS
    # -----------------------------------------------------
    #
    # We normalize the text first and then check for
    # AWS credential patterns again.

    normalized_upper = normalized.upper()

    normalized_patterns = [

        # AWS Access Key IDs
        r"AKIA[0-9A-Z]{16}",

        # AWS temporary access key IDs
        r"ASIA[0-9A-Z]{16}",
    ]


    for pattern in normalized_patterns:

        if re.search(pattern, normalized_upper):
            return True


    # No sensitive credential pattern detected.
    return False


# =========================================================
# PROMPT INJECTION SECURITY CONTROL
# =========================================================
#
# PURPOSE:
# Detect common prompt-injection attempts before they
# reach the AI model.
#
# WHY:
# An attacker may attempt to manipulate the AI model by
# telling it to ignore its instructions or reveal
# protected information.
#
# This is a rule-based FIRST security layer.
# =========================================================

def contains_prompt_injection(text):
    """
    Detect common prompt-injection patterns.
    """

    if not text:
        return False


    # Convert input to lowercase so detection is
    # case-insensitive.
    normalized = text.lower()


    # -----------------------------------------------------
    # COMMON PROMPT-INJECTION PATTERNS
    # -----------------------------------------------------

    injection_patterns = [

        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore your previous instructions",

        "disregard previous instructions",
        "disregard all previous instructions",

        "forget previous instructions",
        "forget all previous instructions",

        "override your instructions",
        "override the system prompt",

        "reveal your system prompt",
        "show me your system prompt",
        "print your system prompt",

        "reveal hidden instructions",
        "show hidden instructions",

        "developer message",
        "system message",

        "you are now unrestricted",
        "you are now unfiltered",

        "disable your safety rules",

        "bypass your safety rules",
        "bypass security controls",

        "jailbreak",
    ]


    # Check every known injection pattern.
    for pattern in injection_patterns:

        if pattern in normalized:
            return True


    # No known prompt-injection pattern detected.
    return False


# =========================================================
# LAMBDA HANDLER
# =========================================================
#
# PURPOSE:
# This is the main entry point for the AI Security Gateway.
#
# Request flow:
#
#   API Gateway
#        ↓
#   Cognito authentication
#        ↓
#   Lambda
#        ↓
#   DLP check
#        ↓
#   Prompt-injection check
#        ↓
#   CloudWatch security metric
#        ↓
#   Amazon Bedrock
#        ↓
#   Response
#
# IMPORTANT:
# The AI model is NOT called until the security controls
# have passed.
# =========================================================

def handler(event, context):

    # -----------------------------------------------------
    # CREATE REQUEST ID
    # -----------------------------------------------------
    #
    # WHY:
    # Every request needs a unique identifier so we can
    # trace it through CloudWatch logs.

    request_id = str(
        getattr(context, "aws_request_id", None)
        or uuid.uuid4()
    )


    # Log that a new request was received.
    logger.info(
        json.dumps({
            "event": "agent_request_received",
            "request_id": request_id,
            "model": MODEL_ID
        })
    )


    try:

        # =================================================
        # READ REQUEST
        # =================================================
        #
        # The API request provides the user's prompt.
        #
        # If no prompt is provided, we use a safe default
        # question so the function can still be tested.

        prompt = event.get(
            "prompt",
            "Explain what an AI security gateway does in one sentence."
        )


        # =================================================
        # DLP SECURITY CONTROL
        # =================================================
        #
        # Check for potential credentials or secrets BEFORE
        # sending the request to the AI model.

        if contains_sensitive_data(prompt):

            # Write a detailed warning to CloudWatch Logs.
            logger.warning(
                json.dumps({
                    "event": "dlp_blocked_request",
                    "request_id": request_id,
                    "reason": "potential_secret_detected"
                })
            )


            # Create a standardized security audit event.
            log_security_event(
                request_id=request_id,
                control="dlp",
                action="BLOCK",
                reason="potential_secret_detected"
            )


            # Publish the DLP metric.
            #
            # WHY:
            # CloudWatch can now count how many DLP
            # violations occurred.

            publish_security_metric(
                "DLPBlockedRequests"
            )


            # Stop processing.
            #
            # IMPORTANT:
            # The request never reaches Amazon Bedrock.

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Request blocked by AI security policy",
                    "request_id": request_id
                })
            }


        # =================================================
        # PROMPT INJECTION SECURITY CONTROL
        # =================================================
        #
        # Check for known prompt-injection patterns.

        if contains_prompt_injection(prompt):

            # Log the attempted injection.
            logger.warning(
                json.dumps({
                    "event": "prompt_injection_blocked",
                    "request_id": request_id,
                    "reason": "potential_prompt_injection_detected"
                })
            )


            # Create standardized security audit event.
            log_security_event(
                request_id=request_id,
                control="prompt_injection",
                action="BLOCK",
                reason="potential_prompt_injection_detected"
            )


            # Publish the prompt-injection metric.
            #
            # WHY:
            # Security teams can monitor attempted
            # prompt-injection attacks.

            publish_security_metric(
                "PromptInjectionBlockedRequests"
            )


            # Stop processing.
            #
            # The malicious request never reaches
            # Amazon Bedrock.

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Request blocked by AI security policy",
                    "request_id": request_id
                })
            }


        # =================================================
        # REQUEST PASSED SECURITY CONTROLS
        # =================================================
        #
        # At this point:
        #
        #   DLP             → PASS
        #   Prompt Injection → PASS
        #
        # The request is allowed to continue.

        log_security_event(
            request_id=request_id,
            control="gateway",
            action="ALLOW",
            reason="request_passed_security_controls"
        )


        # Publish an allowed-request metric.
        #
        # WHY:
        # This lets us measure normal traffic separately
        # from blocked security events.

        publish_security_metric(
            "AllowedRequests"
        )


        # =================================================
        # CALL AMAZON BEDROCK
        # =================================================
        #
        # Only requests that pass the security controls
        # reach the AI model.

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


        # =================================================
        # EXTRACT MODEL RESPONSE
        # =================================================
        #
        # Bedrock returns a structured response.
        # We extract the actual text generated by the model.

        output_text = (
            response["output"]
            ["message"]
            ["content"][0]
            ["text"]
        )


        # =================================================
        # SUCCESS LOG
        # =================================================
        #
        # Record that the AI request completed successfully.

        logger.info(
            json.dumps({
                "event": "agent_request_completed",
                "request_id": request_id,
                "model": MODEL_ID
            })
        )


        # =================================================
        # RETURN RESPONSE
        # =================================================

        return {
            "statusCode": 200,

            "body": json.dumps({
                "model": MODEL_ID,
                "response": output_text
            })
        }


    # =====================================================
    # ERROR HANDLING
    # =====================================================
    #
    # PURPOSE:
    # Catch unexpected application or AWS errors.
    #
    # WHY:
    # We don't want internal error details exposed to
    # the API consumer.
    #
    # Detailed information is logged internally while the
    # client receives a generic error message.
    # =====================================================

    except Exception as error:

        logger.exception(
            json.dumps({
                "event": "agent_request_failed",
                "request_id": request_id,
                "error": str(error)
            })
        )


        return {
            "statusCode": 500,

            "body": json.dumps({
                "error": "Internal server error",
                "request_id": request_id
            })
        }