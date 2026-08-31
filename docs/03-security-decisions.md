# Security Decisions

## Decision 001 — Resource Tagging

### Decision

All Terraform-managed resources should use standardized project,
environment, ownership, and management tags.

### Why

Standardized tagging helps with:

- Resource identification
- Cost management
- Incident investigation
- Automation
- Compliance evidence
- Resource lifecycle management

### Standard Tags

- Project
- Environment
- ManagedBy
- Owner

### Implementation

Tags are defined centrally in `locals.tf` and reused across resources.

### Status

Approved




## Decision 002 — AI Workload Least Privilege

### Requirement

The AI workload must read approved AI data from the
NextGen S3 data store.

### Decision

The workload will use an IAM role with only the permissions
required for its function.

### Allowed

- Read approved S3 objects

### Not Allowed

- IAM administration
- S3 administration
- Bucket deletion
- Access to unrelated AWS resources
- Administrator privileges

### Security Goal

Limit the blast radius if the AI workload is compromised.

### Principle

Least privilege.

### Status

Approved