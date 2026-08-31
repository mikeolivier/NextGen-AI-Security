# NextGen AI Security & DLP Platform
# Security Controls Matrix

## 1. Purpose

This document maps identified threats to security controls, AWS services, Terraform modules, validation tests, and evidence.

Every major security requirement must have a corresponding control and test.

---

# 2. Security Control Matrix

| ID | Threat | Security Control | AWS / Technology | Terraform Module | Validation |
|---|---|---|---|---|---|
| IAM-01 | Excessive permissions | Least-privilege IAM | AWS IAM | iam | IAM simulation |
| IAM-02 | Credential compromise | Workload IAM roles | AWS IAM | iam | Role validation |
| DATA-01 | Data exposure | S3 public access blocking | S3 | s3 | Public access test |
| DATA-02 | Data theft | Encryption at rest | S3 / KMS | s3 / kms | Encryption validation |
| DATA-03 | Data recovery | Versioning | S3 | s3 | Versioning test |
| DLP-01 | PII leakage | Input PII detection | DLP engine | dlp | PII test |
| DLP-02 | Sensitive data leakage | Data classification | DLP engine | dlp | Classification test |
| DLP-03 | AI output leakage | Output DLP | DLP engine | dlp | Output test |
| AI-01 | Prompt injection | Prompt inspection | AI Security Gateway | ai-gateway | Injection test |
| AI-02 | Agent manipulation | Agent policy enforcement | AI Agent | lambda / agent | Agent test |
| AI-03 | Tool abuse | Tool authorization | IAM / application controls | iam | Unauthorized tool test |
| AI-04 | Excessive tool access | Least privilege | IAM | iam | IAM simulation |
| LOG-01 | Blind spots | Cloud activity logging | CloudTrail | logging | Log validation |
| LOG-02 | Missing application telemetry | Application logging | CloudWatch | logging | Log validation |
| DET-01 | Threats not detected | Detection rules | CloudWatch / security services | detection | Detection test |
| ALERT-01 | Delayed response | Security alerting | SNS / CloudWatch | alerting | Alert test |
| IR-01 | Slow response | Incident response playbooks | SOC procedures | security | IR exercise |
| SEC-01 | Public exposure | Continuous security validation | AWS / Terraform | tests | Security test |
| SEC-02 | Infrastructure drift | IaC management | Terraform | all modules | Terraform plan |
| COMP-01 | Missing evidence | Security evidence collection | AWS logs / reports | evidence | Evidence review |

---

# 3. IAM Controls

## IAM-01 — Least Privilege

### Objective

Ensure workloads receive only the permissions required to perform their function.

### Current implementation

The AI workload role currently has:

```text
s3:GetObject