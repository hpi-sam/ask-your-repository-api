from doublex import method_returning
from doublex_expects import have_been_called
from expects import expect, contain
from mamba import description, before, it

from application.models.artifact_builder import ArtifactBuilder
from application.recognition.image_recognition import ImageRecognizer
from specs.factories.image_recognition import vision_api_response
from specs.spec_helpers import Context

with description('image recognition called during create') as self:
    with before.each:
        self.context = Context()
        self.recognizer = ImageRecognizer
        builder = ArtifactBuilder()
        self.artifact = builder.build_with(file_url="files/test.jpg", tags=['test'],
                                           user_tags=['test'])
        self.recognizer._call_google_api = method_returning(vision_api_response())

    with it('Adds Tags to artifact'):
        self.recognizer._work_asynchronously(self.artifact)
        expect(self.recognizer._call_google_api).to(have_been_called.once)
        expect(list(map(lambda x: x.name, self.artifact.tags))).to(
            contain("Arne", "Zerndt", "Meeting"))
