---
description:
---

# CityPulse Project Completion Audit Prompt

Perform a comprehensive audit of the CityPulse project to validate all completed tasks marked as
"done" in the task.json file:

**STEP 1: Parse and Analyze Task Status**

- Read and parse the task.json file from the project root
- Identify all tasks marked with status: "done"
- List all subtasks within completed tasks and their status
- Create a completion summary report showing:
  - Total tasks vs completed tasks
  - Pending tasks and their dependencies
  - Any inconsistencies in task status

**STEP 2: Verify Infrastructure Completeness (Task 1)** If marked as "done", validate:

- Google Cloud Project exists and is properly configured
- All required APIs are enabled (Pub/Sub, Dataflow, BigQuery, Firestore, etc.)
- IAM roles and permissions are correctly set up
- VPC, encryption, and audit logging are configured
- Run verification commands:
  ```bash
  gcloud services list --enabled
  gcloud iam roles list --project=PROJECT_ID
  gcloud logging logs list
  ```

**STEP 3: Validate Data Models Implementation (Task 2)** If marked as "done", check:

- BigQuery tables exist with correct schema and partitioning
- Firestore collections are properly structured
- Data types, indexes, and constraints are implemented
- Schema validation functions are working
- Run validation queries:
  ```sql
  SELECT table_name, table_type FROM `project.dataset.INFORMATION_SCHEMA.TABLES`
  ```

**STEP 4: Test Data Ingestion Pipelines (Task 3)** If marked as "done", verify:

- Pub/Sub topics exist and are functional
- Dataflow pipelines are deployed and running
- Data flows correctly from sources to BigQuery/Firestore
- Error handling and replay mechanisms work
- Run pipeline tests:
  ```bash
  gcloud pubsub topics list
  gcloud dataflow jobs list
  # Test message publishing and consumption
  ```

**STEP 5: Validate AI Processing Implementation (Task 7)** If marked as "done", test:

- Vertex AI integrations are functional
- Text processing with Gemini works correctly
- Image/video analysis with Vision API is operational
- Generated insights are stored properly
- Run AI processing tests:
  ```bash
  # Test Gemini text processing
  # Test Vision API image analysis
  # Validate AI insights storage
  ```

**STEP 6: Comprehensive Integration Testing** For all completed tasks, perform:

1. **End-to-End Data Flow Test:**
   - Submit a test citizen report with text and image
   - Verify it flows through: Ingestion → AI Processing → Storage
   - Check that all metadata and insights are generated
   - Validate data appears in both BigQuery and Firestore

2. **API Functionality Test:**
   - Test all implemented endpoints (if Task 4 is done)
   - Verify authentication and authorization
   - Test CRUD operations on events, users, feedback
   - Validate error handling and rate limiting

3. **Performance and Load Testing:**
   - Test system under simulated load
   - Verify response times meet requirements
   - Check memory usage and resource consumption
   - Validate auto-scaling behavior

4. **Security and Compliance Testing:**
   - Verify all security measures are active
   - Test access controls and permissions
   - Validate audit logging functionality
   - Check data encryption at rest and in transit

**STEP 7: Generate Comprehensive Audit Report** Create a detailed report including:

1. **Completion Status Matrix:**

   ```
   Task ID | Task Name | Status | Verification Result | Issues Found
   --------|-----------|--------|-------------------|-------------
   1       | GCP Setup | Done   | ✅ Verified        | None
   2       | Data Models| Done   | ❌ Failed         | Missing indexes
   ```

2. **Failed Verification Details:**
   - Specific issues found in each task
   - Missing components or configurations
   - Performance bottlenecks identified
   - Security vulnerabilities discovered

3. **Recommendations:**
   - Immediate fixes required for failed verifications
   - Performance optimization suggestions
   - Security enhancement recommendations
   - Documentation updates needed

4. **Test Results Summary:**
   - Total tests run vs passed/failed
   - Performance metrics (response times, throughput)
   - Error logs and debugging information
   - Coverage analysis for completed features

**STEP 8: Automated Fix Suggestions** For each failed verification, provide:

- Specific commands to run for fixes
- Code snippets to implement missing features
- Configuration updates required
- Step-by-step remediation guides

**STEP 9: Regression Testing** After any fixes are applied:

- Re-run all verification tests
- Ensure fixes don't break existing functionality
- Update task.json status if needed
- Generate final completion report

**OUTPUT FORMAT:**

```json
{
  "audit_timestamp": "2025-07-05T10:30:00Z",
  "project_status": {
    "total_tasks": 10,
    "completed_tasks": 3,
    "verified_tasks": 2,
    "failed_verifications": 1
  },
  "verification_results": [
    {
      "task_id": 1,
      "task_name": "Setup Core GCP Infrastructure",
      "claimed_status": "done",
      "verification_status": "passed",
      "issues": [],
      "recommendations": []
    }
  ],
  "critical_issues": [
    "Missing BigQuery table indexes affecting query performance",
    "Firestore security rules not properly configured"
  ],
  "next_actions": [
    "Fix Firestore security rules",
    "Add missing BigQuery indexes",
    "Re-run verification tests"
  ]
}
```

**EXECUTION PRIORITY:**

1. Run this audit before starting any new tasks
2. Fix all critical issues before proceeding
3. Update task.json file with accurate status
4. Re-run audit after fixes to ensure completeness

This comprehensive audit ensures that all "done" tasks are truly complete and production-ready.
