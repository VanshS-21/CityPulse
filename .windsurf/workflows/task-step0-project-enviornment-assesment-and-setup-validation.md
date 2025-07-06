---
description:
---

Analyze the current project environment and assess readiness for the upcoming task:

Perform a comprehensive environment assessment:

1. **Project Structure Analysis:**
   - Scan the current directory structure and identify existing folders
   - Check for presence of key project files (package.json, requirements.txt, etc.)
   - Verify if standard project conventions are being followed
   - Identify any missing critical directories or files

2. **Dependency and Prerequisites Check:**
   - Verify if prerequisite tasks have been completed (check for their deliverables)
   - Validate that required dependencies are installed and configured
   - Check for environment configuration files (.env, config files)
   - Confirm database connections and external service integrations exist

3. **Technology Stack Validation:**
   - Identify currently installed frameworks and libraries
   - Check version compatibility and update requirements
   - Verify development tools and CLI installations
   - Validate cloud service configurations (GCP, Firebase, etc.)

4. **Code Quality and Standards Assessment:**
   - Check for existing linting and formatting configurations
   - Verify testing framework setup and existing test coverage
   - Assess current code structure and architectural patterns
   - Identify any technical debt or inconsistencies

5. **Environment Readiness Classification:**
   - **GREEN (Ready):** All prerequisites met, can proceed directly to implementation
   - **YELLOW (Partial):** Some setup exists but requires updates/additions
   - **RED (Not Ready):** Significant setup required before task implementation

6. **Generate Setup Action Plan:**
   - List specific files/folders that need to be created
   - Identify missing dependencies that need installation
   - Specify configuration updates required
   - Prioritize setup tasks based on complexity and dependencies

7. **Provide Immediate Next Steps:**
   - If GREEN: Proceed to Prompt 1 with current environment
   - If YELLOW: Execute specific setup commands and file creation
   - If RED: Complete full environment setup before task implementation

**Output Format:**
- Environment Status: [GREEN/YELLOW/RED]
- Missing Components: [List of missing items]
- Setup Commands: [Specific commands to run]
- Files to Create: [List of files and their purposes]
- Estimated Setup Time: [Time estimate for environment preparation]

This assessment will ensure optimal task execution with minimal setup interruptions.
