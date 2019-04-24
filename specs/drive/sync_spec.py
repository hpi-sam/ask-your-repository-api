from googleapiclient.http import HttpMockSequence
from mamba import description, before, it

from application.teams.placeholder_drives.drive import Drive
from application.teams.placeholder_drives.sync import ImageSynchronizer
from specs.factories.image_recognition import mock_image_recognition
from specs.spec_helpers import Context

with description("drive") as self:
    with before.each:
        self.context = Context()


    # generating discovery file:
    #        with open("drive-discovery.json", "w") as f:
    #            f.write(_retrieve_discovery_doc("https://www.googleapis.com/discovery/v1/apis/drive/v3/rest", build_http(), cache_discovery=False))
    def file_content(path):
        return open(path).read()


    with description("downloading"):
        with it("downloads something"):
            with mock_image_recognition:
                # http = HttpMock('drive-discovery.json', {'status': '200'})
                #http = HttpMockSequence([({'status': 200}, file_content('drive-discovery.json')),
                #                         ({'status': 200}, file_content('drive-list.json'))])
                api_key = 'your_api_key'
                sync = ImageSynchronizer(Drive.all()[3])
                print(sync.upload_all_missing())

    #
