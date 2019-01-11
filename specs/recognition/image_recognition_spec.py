from flask import current_app
from mamba import description, before, it
from expects import expect, be_none
from doublex import Mock, ANY_ARG
from specs.spec_helpers import Context
from application.controllers.artifacts_controller import no_content
from application.recognition.image_recognition import _work_asynchronously
from specs.factories.image_recognition import vision_api_response
from unittest.mock import patch

with description('image recognition called during create') as self:
    with before.each:
        self.context = Context()
        with Mock() as artifact_mock:
            artifact_mock.update(ANY_ARG).returns(no_content())
            artifact_mock.tags = []
        self.artifact = artifact_mock
    with it('Adds Tags to artifact'):
        with patch('application.recognition.image_recognition._call_google_api',
                   return_value=vision_api_response()):
            expect(_work_asynchronously('files.askir.me/test.jpg', self.artifact)).to(be_none)
