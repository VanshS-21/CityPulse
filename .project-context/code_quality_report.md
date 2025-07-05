# Code Quality Report

This report details the findings from the `pylint` analysis of the Python codebase. The overall code quality score is **6.97/10**.

## Summary of Issues

*   **Errors (E):** Critical issues that are likely bugs and should be fixed immediately.
*   **Warnings (W):** Important issues that could lead to unexpected behavior or bugs.
*   **Refactoring (R):** Suggestions for code improvements to enhance readability and maintainability.
*   **Convention (C):** Violations of the PEP 8 style guide.

## Detailed Pylint Output

```
************* Module data_models.setup_bigquery_tables
data_models\setup_bigquery_tables.py:15:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\setup_bigquery_tables.py:27:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\setup_bigquery_tables.py:42:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\setup_bigquery_tables.py:72:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\setup_bigquery_tables.py:74:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\setup_bigquery_tables.py:80:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\setup_bigquery_tables.py:95:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\setup_bigquery_tables.py:13:9: W1514: Using open without explicitly specifying an encoding (unspecified-encoding)
data_models\setup_bigquery_tables.py:39:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
data_models\setup_bigquery_tables.py:67:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module data_models.validate_schemas
data_models\validate_schemas.py:30:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\validate_schemas.py:51:0: C0301: Line too long (104/100) (line-too-long)
data_models\validate_schemas.py:99:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\validate_schemas.py:28:15: W0718: Catching too general exception Exception (broad-exception-caught)
data_models\validate_schemas.py:22:17: W1514: Using open without explicitly specifying an encoding (unspecified-encoding)
data_models\validate_schemas.py:7:0: R0903: Too few public methods (1/2) (too-few-public-methods)
data_models\validate_schemas.py:102:8: R1722: Consider using 'sys.exit' instead (consider-using-sys-exit)
************* Module data_models.data_ingestion.ai_processing
data_models\data_ingestion\ai_processing.py:65:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\data_ingestion\ai_processing.py:77:0: C0301: Line too long (177/100) (line-too-long)
data_models\data_ingestion\ai_processing.py:84:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\data_ingestion\ai_processing.py:94:0: C0301: Line too long (117/100) (line-too-long)
data_models\data_ingestion\ai_processing.py:66:17: W0511: TODO: Add more robust parsing and error handling for the response (fixme)
data_models\data_ingestion\ai_processing.py:14:0: W0223: Method 'process_batch' is abstract in class 'DoFn' but is not overridden in child class 'ProcessWithAI' (abstract-method)
data_models\data_ingestion\ai_processing.py:14:0: W0223: Method 'to_runner_api_parameter' is abstract in class 'RunnerApiFn' but is not overridden in child class 'ProcessWithAI' (abstract-method)
data_models\data_ingestion\ai_processing.py:17:4: W0231: __init__ method from base class 'DoFn' is not called (super-init-not-called)
data_models\data_ingestion\ai_processing.py:25:58: E1101: Module 'data_models.core.config' has no 'GCP_REGION' member (no-member)
data_models\data_ingestion\ai_processing.py:29:49: E1101: Module 'data_models.core.config' has no 'GCS_GENERATED_IMAGES_BUCKET' member (no-member)
data_models\data_ingestion\ai_processing.py:31:4: W0221: Variadics removed in overriding 'ProcessWithAI.process' method (arguments-differ)
data_models\data_ingestion\ai_processing.py:31:4: R0914: Too many local variables (16/15) (too-many-locals)
data_models\data_ingestion\ai_processing.py:98:15: W0718: Catching too general exception Exception (broad-exception-caught)
data_models\data_ingestion\ai_processing.py:61:27: W0718: Catching too general exception Exception (broad-exception-caught)
data_models\data_ingestion\ai_processing.py:59:32: E1101: Class 'Image' has no 'load_from_uri' member (no-member)
data_models\data_ingestion\ai_processing.py:62:24: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
data_models\data_ingestion\ai_processing.py:67:30: E0602: Undefined variable 'json' (undefined-variable)
data_models\data_ingestion\ai_processing.py:93:27: W0718: Catching too general exception Exception (broad-exception-caught)
data_models\data_ingestion\ai_processing.py:87:42: W0212: Access to a protected member _image_bytes of a client class (protected-access)
data_models\data_ingestion\ai_processing.py:94:24: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
data_models\data_ingestion\ai_processing.py:99:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
************* Module data_models.data_ingestion.base_pipeline
data_models\data_ingestion\base_pipeline.py:81:0: C0301: Line too long (114/100) (line-too-long)
data_models\data_ingestion\base_pipeline.py:84:0: C0301: Line too long (101/100) (line-too-long)
data_models\data_ingestion\base_pipeline.py:122:0: C0301: Line too long (110/100) (line-too-long)
data_models\data_ingestion\base_pipeline.py:1:0: C0114: Missing module docstring (missing-module-docstring)
data_models\data_ingestion\base_pipeline.py:34:0: W0223: Method 'process_batch' is abstract in class 'DoFn' but is not overridden in child class 'ParseEvent' (abstract-method)
data_models\data_ingestion\base_pipeline.py:34:0: W0223: Method 'to_runner_api_parameter' is abstract in class 'RunnerApiFn' but is not overridden in child class 'ParseEvent' (abstract-method)
data_models\data_ingestion\base_pipeline.py:37:4: W0221: Variadics removed in overriding 'ParseEvent.process' method (arguments-differ)
data_models\data_ingestion\base_pipeline.py:43:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
data_models\data_ingestion\base_pipeline.py:47:0: W0223: Method 'process_batch' is abstract in class 'DoFn' but is not overridden in child class 'WriteToFirestore' (abstract-method)
data_models\data_ingestion\base_pipeline.py:47:0: W0223: Method 'to_runner_api_parameter' is abstract in class 'RunnerApiFn' but is not overridden in child class 'WriteToFirestore' (abstract-method)
data_models\data_ingestion\base_pipeline.py:50:4: W0231: __init__ method from base class 'DoFn' is not called (super-init-not-called)
data_models\data_ingestion\base_pipeline.py:57:4: W0221: Variadics removed in overriding 'WriteToFirestore.process' method (arguments-differ)
data_models\data_ingestion\base_pipeline.py:61:15: W0718: Catching too general exception Exception (broad-exception-caught)
data_models\data_ingestion\base_pipeline.py:62:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
data_models\data_ingestion\base_pipeline.py:94:13: W1514: Using open without explicitly specifying an encoding (unspecified-encoding)
data_models\data_ingestion\base_pipeline.py:108:12: W0106: Expression "all_dead_letters | 'Log Dead-Letter' >> beam.Map(lambda x: logging.error(f'Dead-letter record: {x}'))" is assigned to nothing (expression-not-assigned)
data_models\data_ingestion\base_pipeline.py:109:26: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
data_models\data_ingestion\base_pipeline.py:1:0: W0611: Unused import argparse (unused-import)
************* Module data_models.data_ingestion.citizen_report_pipeline
data_models\data_ingestion\citizen_report_pipeline.py:18:0: C0301: Line too long (116/100) (line-too-long)
data_models\data_ingestion\citizen_report_pipeline.py:1:0: C0114: Missing module docstring (missing-module-docstring)
data_models\data_ingestion\citizen_report_pipeline.py:18:77: E1101: Module 'data_models.core.config' has no 'BIGQUERY_TABLE_CITIZEN_REPORTS' member (no-member)
data_models\data_ingestion\citizen_report_pipeline.py:37:0: W0223: Method 'process_batch' is abstract in class 'DoFn' but is not overridden in child class 'ProcessMultimedia' (abstract-method)
data_models\data_ingestion\citizen_report_pipeline.py:37:0: W0223: Method 'to_runner_api_parameter' is abstract in class 'RunnerApiFn' but is not overridden in child class 'ProcessMultimedia' (abstract-method)
data_models\data_ingestion\citizen_report_pipeline.py:40:4: W0231: __init__ method from base class 'DoFn' is not called (super-init-not-called)
data_models\data_ingestion\citizen_report_pipeline.py:51:4: W0221: Variadics removed in overriding 'ProcessMultimedia.process' method (arguments-differ)
data_models\data_ingestion\citizen_report_pipeline.py:75:15: W0718: Catching too general exception Exception (broad-exception-caught)
data_models\data_ingestion\citizen_report_pipeline.py:76:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
************* Module data_models.data_ingestion.iot_pipeline
data_models\data_ingestion\iot_pipeline.py:15:0: C0301: Line too long (104/100) (line-too-long)
data_models\data_ingestion\iot_pipeline.py:39:0: C0301: Line too long (106/100) (line-too-long)
data_models\data_ingestion\iot_pipeline.py:1:0: C0114: Missing module docstring (missing-module-docstring)
data_models\data_ingestion\iot_pipeline.py:15:77: E1101: Module 'data_models.core.config' has no 'BIGQUERY_TABLE_IOT' member (no-member)
************* Module data_models.data_ingestion.official_feeds_pipeline
data_models\data_ingestion\official_feeds_pipeline.py:12:0: C0301: Line too long (115/100) (line-too-long)
data_models\data_ingestion\official_feeds_pipeline.py:1:0: C0114: Missing module docstring (missing-module-docstring)
data_models\data_ingestion\official_feeds_pipeline.py:12:77: E1101: Module 'data_models.core.config' has no 'BIGQUERY_TABLE_OFFICIAL_FEEDS' member (no-member)
************* Module data_models.data_ingestion.social_media_pipeline
data_models\data_ingestion\social_media_pipeline.py:18:0: C0301: Line too long (113/100) (line-too-long)
data_models\data_ingestion\social_media_pipeline.py:60:0: C0301: Line too long (116/100) (line-too-long)
data_models\data_ingestion\social_media_pipeline.py:82:0: C0301: Line too long (112/100) (line-too-long)
data_models\data_ingestion\social_media_pipeline.py:1:0: C0114: Missing module docstring (missing-module-docstring)
data_models\data_ingestion\social_media_pipeline.py:18:77: E1101: Module 'data_models.core.config' has no 'BIGQUERY_TABLE_SOCIAL_MEDIA' member (no-member)
data_models\data_ingestion\social_media_pipeline.py:22:20: E1101: Module 'data_models.core.config' has no 'PUBSUB_SOCIAL_MEDIA_TOPIC' member (no-member)
data_models\data_ingestion\social_media_pipeline.py:33:0: W0223: Method 'process_batch' is abstract in class 'DoFn' but is not overridden in child class 'ParseSocialMediaEvent' (abstract-method)
data_models\data_ingestion\social_media_pipeline.py:33:0: W0223: Method 'to_runner_api_parameter' is abstract in class 'RunnerApiFn' but is not overridden in child class 'ParseSocialMediaEvent' (abstract-method)
data_models\data_ingestion\social_media_pipeline.py:36:4: W0221: Variadics removed in overriding 'ParseSocialMediaEvent.process' method (arguments-differ)
data_models\data_ingestion\social_media_pipeline.py:45:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
data_models\data_ingestion\social_media_pipeline.py:49:0: W0223: Method 'process_batch' is abstract in class 'DoFn' but is not overridden in child class 'AnalyzeSentiment' (abstract-method)
data_models\data_ingestion\social_media_pipeline.py:49:0: W0223: Method 'to_runner_api_parameter' is abstract in class 'RunnerApiFn' but is not overridden in child class 'AnalyzeSentiment' (abstract-method)
data_models\data_ingestion\social_media_pipeline.py:52:4: W0231: __init__ method from base class 'DoFn' is not called (super-init-not-called)
data_models\data_ingestion\social_media_pipeline.py:58:4: W0221: Variadics removed in overriding 'AnalyzeSentiment.process' method (arguments-differ)
data_models\data_ingestion\social_media_pipeline.py:65:15: W0718: Catching too general exception Exception (broad-exception-caught)
data_models\data_ingestion\social_media_pipeline.py:66:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
************* Module data_models.firestore_models.base_model
data_models\firestore_models\base_model.py:103:0: C0305: Trailing newlines (trailing-newlines)
************* Module data_models.firestore_models.event
data_models\firestore_models\event.py:87:0: C0305: Trailing newlines (trailing-newlines)
data_models\firestore_models\event.py:34:0: C0115: Missing class docstring (missing-class-docstring)
data_models\firestore_models\event.py:43:0: C0115: Missing class docstring (missing-class-docstring)
data_models\firestore_models\event.py:50:0: C0115: Missing class docstring (missing-class-docstring)
data_models\firestore_models\event.py:56:0: C0115: Missing class docstring (missing-class-docstring)
data_models\firestore_models\event.py:63:0: C0115: Missing class docstring (missing-class-docstring)
data_models\firestore_models\event.py:81:4: C0116: Missing function or method docstring (missing-function-docstring)
************* Module data_models.firestore_models.feedback
data_models\firestore_models\feedback.py:65:0: C0301: Line too long (119/100) (line-too-long)
data_models\firestore_models\feedback.py:101:0: C0301: Line too long (106/100) (line-too-long)
data_models\firestore_models\feedback.py:111:0: C0301: Line too long (103/100) (line-too-long)
************* Module data_models.firestore_models.user_profile
data_models\firestore_models\user_profile.py:95:23: E1135: Value 'self.roles' doesn't support membership test (unsupported-membership-test)
data_models\firestore_models\user_profile.py:104:23: E1135: Value 'self.roles' doesn't support membership test (unsupported-membership-test)
data_models\firestore_models\user_profile.py:105:12: E1101: Instance of 'FieldInfo' has no 'append' member (no-member)
data_models\firestore_models\user_profile.py:114:19: E1135: Value 'self.roles' doesn't support membership test (unsupported-membership-test)
data_models\firestore_models\user_profile.py:115:12: E1101: Instance of 'FieldInfo' has no 'remove' member (no-member)
************* Module data_models.tests.common
data_models\tests\common.py:1:0: C0114: Missing module docstring (missing-module-docstring)
************* Module data_models.tests.conftest
data_models\tests\conftest.py:2:0: W0611: Unused import os (unused-import)
************* Module data_models.tests.test_base_pipeline
data_models\tests\test_base_pipeline.py:61:0: C0301: Line too long (134/100) (line-too-long)
data_models\tests\test_base_pipeline.py:71:0: C0301: Line too long (135/100) (line-too-long)
data_models\tests\test_base_pipeline.py:107:0: C0301: Line too long (103/100) (line-too-long)
data_models\tests\test_base_pipeline.py:1:0: C0114: Missing module docstring (missing-module-docstring)
data_models\tests\test_base_pipeline.py:25:0: C0115: Missing class docstring (missing-class-docstring)
data_models\tests\test_base_pipeline.py:28:4: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_base_pipeline.py:57:4: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_base_pipeline.py:65:4: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_base_pipeline.py:76:0: C0115: Missing class docstring (missing-class-docstring)
data_models\tests\test_base_pipeline.py:79:4: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_base_pipeline.py:94:4: C0116: Missing function or method docstring (missing-function-docstring)
************* Module data_models.tests.test_bigquery_setup
data_models\tests\test_bigquery_setup.py:52:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:59:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:70:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:72:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:91:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:94:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:102:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:105:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:114:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:117:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:125:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_bigquery_setup.py:127:0: C0301: Line too long (102/100) (line-too-long)
data_models\tests\test_bigquery_setup.py:53:13: W0212: Access to a protected member _parse_schema_fields of a client class (protected-access)
data_models\tests\test_bigquery_setup.py:83:22: W0621: Redefining name 'mock_bigquery_client' from outer scope (line 43) (redefined-outer-name)
data_models\tests\test_bigquery_setup.py:111:37: W0621: Redefining name 'mock_bigquery_client' from outer scope (line 43) (redefined-outer-name)
data_models\tests\test_bigquery_setup.py:5:0: C0411: standard import "unittest.mock.MagicMock" should be placed before third party import "pytest" (wrong-import-order)
data_models\tests\test_bigquery_setup.py:2:0: W0611: Unused import os (unused-import)
data_models\tests\test_bigquery_setup.py:5:0: W0611: Unused patch imported from unittest.mock (unused-import)
************* Module data_models.tests.test_citizen_report_pipeline
data_models\tests\test_citizen_report_pipeline.py:67:0: C0301: Line too long (116/100) (line-too-long)
data_models\tests\test_citizen_report_pipeline.py:76:0: C0301: Line too long (115/100) (line-too-long)
data_models\tests\test_citizen_report_pipeline.py:1:0: C0114: Missing module docstring (missing-module-docstring)
data_models\tests\test_citizen_report_pipeline.py:24:0: C0115: Missing class docstring (missing-class-docstring)
data_models\tests\test_citizen_report_pipeline.py:28:4: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_citizen_report_pipeline.py:54:4: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_citizen_report_pipeline.py:66:4: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_citizen_report_pipeline.py:66:78: W0613: Unused argument 'mock_storage_client' (unused-argument)
data_models\tests\test_citizen_report_pipeline.py:10:0: C0412: Imports from package apache_beam are not grouped (ungrouped-imports)
data_models\tests\test_citizen_report_pipeline.py:2:0: W0611: Unused import io (unused-import)
************* Module data_models.tests.test_firestore_models
data_models\tests\test_firestore_models.py:33:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:40:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:56:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:62:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:67:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:84:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:89:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:94:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:114:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:130:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:147:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:155:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:161:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:165:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:173:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_firestore_models.py:13:0: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_firestore_models.py:18:0: C0116: Missing function or method docstring (missing-function-docstring)
data_models\tests\test_firestore_models.py:18:22: W0621: Redefining name 'mock_firestore' from outer scope (line 13) (redefined-outer-name)
data_models\tests\test_firestore_models.py:18:22: W0613: Unused argument 'mock_firestore' (unused-argument)
data_models\tests\test_firestore_models.py:100:40: W0621: Redefining name 'firestore_service' from outer scope (line 18) (redefined-outer-name)
data_models\tests\test_firestore_models.py:100:59: W0621: Redefining name 'mock_firestore' from outer scope (line 13) (redefined-outer-name)
data_models\tests\test_firestore_models.py:121:43: W0621: Redefining name 'firestore_service' from outer scope (line 18) (redefined-outer-name)
data_models\tests\test_firestore_models.py:121:62: W0621: Redefining name 'mock_firestore' from outer scope (line 13) (redefined-outer-name)
data_models\tests\test_firestore_models.py:137:43: W0621: Redefining name 'firestore_service' from outer scope (line 18) (redefined-outer-name)
data_models\tests\test_firestore_models.py:137:62: W0621: Redefining name 'mock_firestore' from outer scope (line 13) (redefined-outer-name)
data_models\tests\test_firestore_models.py:3:0: C0411: standard import "datetime.datetime" should be placed before third party import "pytest" (wrong-import-order)
data_models\tests\test_firestore_models.py:4:0: C0411: standard import "unittest.mock.MagicMock" should be placed before third party import "pytest" (wrong-import-order)
************* Module data_models.tests.test_pipelines
data_models\tests\test_pipelines.py:7:0: C0301: Line too long (106/100) (line-too-long)
data_models\tests\test_pipelines.py:9:0: C0301: Line too long (114/100) (line-too-long)
data_models\tests\test_pipelines.py:10:0: C0301: Line too long (108/100) (line-too-long)
data_models\tests\test_pipelines.py:1:0: C0114: Missing module docstring (missing-module-docstring)
data_models\tests\test_pipelines.py:18:37: E1101: Instance of 'BasePipelineTest' has no 'pipeline_class' member (no-member)
data_models\tests\test_pipelines.py:19:39: E1101: Instance of 'BasePipelineTest' has no 'pipeline_class' member (no-member)
data_models\tests\test_pipelines.py:26:28: E1101: Instance of 'BasePipelineTest' has no 'pipeline_class' member (no-member)
data_models\tests\test_pipelines.py:26:61: E1101: Instance of 'BasePipelineTest' has no 'options_class' member (no-member)
data_models\tests\test_pipelines.py:31:0: C0115: Missing class docstring (missing-class-docstring)
data_models\tests\test_pipelines.py:38:0: C0115: Missing class docstring (missing-class-docstring)
data_models\tests\test_pipelines.py:45:0: C0115: Missing class docstring (missing-class-docstring)
data_models\tests\test_pipelines.py:52:0: C0115: Missing class docstring (missing-class-docstring)
data_models\tests\test_pipelines.py:3:0: W0611: Unused MagicMock imported from unittest.mock (unused-import)
data_models\tests\test_pipelines.py:5:0: W0611: Unused TestPipeline imported from apache_beam.testing.test_pipeline as BeamTestPipeline (unused-import)
************* Module data_models.tests.test_schema_validation
data_models\tests\test_schema_validation.py:38:91: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:40:43: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:42:36: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:44:45: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:46:77: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:48:73: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:50:92: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:52:110: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:52:0: C0301: Line too long (110/100) (line-too-long)
data_models\tests\test_schema_validation.py:54:91: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:76:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:94:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:115:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:118:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:121:0: C0303: Trailing whitespace (trailing-whitespace)
data_models\tests\test_schema_validation.py:65:31: W0621: Redefining name 'temp_schema_file' from outer scope (line 59) (redefined-outer-name)
data_models\tests\test_schema_validation.py:2:0: W0611: Unused import os (unused-import)
************* Module data_models.tests.__init__
data_models\tests\__init__.py:1:0: R0801: Similar lines in 2 files
==data_models.tests.test_bigquery_setup:[27:44]
==data_models.tests.test_schema_validation:[21:36]
        },
        {
            "name": "nested",
            "type": "RECORD",
            "fields": [
                {
                    "name": "nested_field",
                    "type": "STRING"
                }
            ]
        }
    ]
}

@pytest.fixture
def mock_bigquery_client():
    """Create a mock BigQuery client.""" (duplicate-code)
data_models\tests\__init__.py:1:0: R0801: Similar lines in 2 files
==data_models.data_ingestion.official_feeds_pipeline:[16:26]
==data_models.data_ingestion.social_media_pipeline:[22:32]
        parser.add_argument(
            '--output_table',
            help='BigQuery table to write to.',
            default=output_table_name)
        parser.add_argument(
            '--schema_path',
            help='Path to the BigQuery schema file.',
            default='data_models/schemas/event_schema.json')

 (duplicate-code)
data_models\tests\__init__.py:1:0: R0801: Similar lines in 2 files
==data_models.data_ingestion.citizen_report_pipeline:[22:30]
==data_models.data_ingestion.iot_pipeline:[19:29]
        parser.add_argument(
            '--output_table',
            help='BigQuery table to write to.',
            default=output_table_name)
        parser.add_argument(
            '--schema_path',
            help='Path to the BigQuery schema file.',
            default='data_models/schemas/event_schema.json')

 (duplicate-code)
data_models\tests\__init__.py:1:0: R0801: Similar lines in 2 files
==data_models.firestore_models.__init__:[9:14]
==data_models:[8:13]
__all__ = [
    'Event',
    'UserProfile',
    'Feedback',
    'FeedbackStatus', (duplicate-code)
```
