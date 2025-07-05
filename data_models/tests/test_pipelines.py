"""Unit tests for the main pipeline classes."""
import logging
import unittest
from unittest.mock import patch

from data_models.data_ingestion.citizen_report_pipeline import (
    CitizenReportOptions, CitizenReportPipeline)
from data_models.data_ingestion.iot_pipeline import (
    IotPipeline, IotPipelineOptions)
from data_models.data_ingestion.official_feeds_pipeline import (
    OfficialFeedsPipeline, OfficialFeedsPipelineOptions)
from data_models.data_ingestion.social_media_pipeline import (
    SocialMediaPipeline, SocialMediaPipelineOptions)


class BasePipelineTest(unittest.TestCase):
    """Base class for pipeline tests with common mocking logic."""
    __test__ = False
    pipeline_class = None
    options_class = None

    def setUp(self):
        """Set up mock objects for pipeline building and running."""
        self.mock_run = patch.object(self.pipeline_class, 'run').start()
        patch.object(self.pipeline_class, 'build_pipeline').start()

    def tearDown(self):
        """Stop all patches."""
        patch.stopall()

    def test_pipeline_instantiation_and_run(self):
        """Test that the pipeline can be instantiated and that run() is called."""
        pipeline_instance = self.pipeline_class.from_options(self.options_class)
        pipeline_instance.run()
        self.mock_run.assert_called_once()


class TestOfficialFeedsPipeline(BasePipelineTest):
    """Tests for the OfficialFeedsPipeline."""
    __test__ = True

    def setUp(self):
        """Set up the test for OfficialFeedsPipeline."""
        self.pipeline_class = OfficialFeedsPipeline
        self.options_class = OfficialFeedsPipelineOptions
        super().setUp()


class TestCitizenReportPipeline(BasePipelineTest):
    """Tests for the CitizenReportPipeline."""
    __test__ = True

    def setUp(self):
        """Set up the test for CitizenReportPipeline."""
        self.pipeline_class = CitizenReportPipeline
        self.options_class = CitizenReportOptions
        super().setUp()


class TestIotPipeline(BasePipelineTest):
    """Tests for the IotPipeline."""
    __test__ = True

    def setUp(self):
        """Set up the test for IotPipeline."""
        self.pipeline_class = IotPipeline
        self.options_class = IotPipelineOptions
        super().setUp()


class TestSocialMediaPipeline(BasePipelineTest):
    """Tests for the SocialMediaPipeline."""
    __test__ = True

    def setUp(self):
        """Set up the test for SocialMediaPipeline."""
        self.pipeline_class = SocialMediaPipeline
        self.options_class = SocialMediaPipelineOptions
        super().setUp()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()
