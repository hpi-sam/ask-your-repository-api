from doublex import Mock, ANY_ARG, method_returning
from doublex_expects import have_been_called
from expects import expect
from mamba import description, before, it

from application.controllers.artifacts_controller import no_content
from application.recognition.image_recognition import ImageRecognizer
from specs.factories.image_recognition import vision_api_response
from specs.spec_helpers import Context

with description('image recognition called during create') as self:
    with before.each:
        self.context = Context()
        self.recognizer = ImageRecognizer
        with Mock() as artifact_mock:
            artifact_mock.update(ANY_ARG).returns(no_content())
            artifact_mock.tags = []
            artifact_mock.file_url = 'files.askir.me/test.jpg'
        self.artifact = artifact_mock
        self.recognizer._call_google_api = method_returning(vision_api_response())
    with it('Adds Tags to artifact'):
        self.recognizer._work_asynchronously(self.artifact)
        expect(self.recognizer._call_google_api).to(have_been_called.once)
        expect(self.artifact.update).to(have_been_called.once)
