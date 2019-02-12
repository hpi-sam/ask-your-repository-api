from doublex import method_returning
from doublex_expects import have_been_called
from expects import expect, contain
from mamba import description, before, it

from application.models import Artifact
from application.recognition.image_recognition import ImageRecognizer
from specs.factories.image_recognition import vision_api_response
from specs.spec_helpers import Context

with description('image recognition called during create') as self:
    with before.each:
        self.context = Context()
        self.recognizer = ImageRecognizer
        self.artifact = Artifact(file_url="files.askir.me/test.jpg").save()
        self.recognizer._call_google_api = method_returning(vision_api_response())

    with it('Adds Tags to artifact'):
        self.recognizer._work_asynchronously(self.artifact)
        expect(self.recognizer._call_google_api).to(have_been_called.once)
        expect(self.artifact.tags_list).to(contain("Arne", "Zerndt", "Meeting"))
