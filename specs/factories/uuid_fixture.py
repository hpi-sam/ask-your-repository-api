"""Manages uuids for tests in one file"""
UUIDS = [
    'dc5434f4-1239-41b2-87a1-c8df49f94ab2',
    '07cbbc92-78ec-4470-805b-d740aa504e9a',
    'eff808ea-285d-4b72-a886-63720ae83106',
    'd965f0f7-3ebf-4c3c-a7f6-86ff76e2d8ba',
    'e23f2d51-990a-45e0-9d7a-e528c1c3ef63',
    '3f9a3c7f-cb14-4f40-b3bd-e49206e31fd5',
    '83e8db8f-fb68-4c30-a44e-c1b9ef62d928',
    'd282db7a-3a27-49fb-9586-353662ed2d2e',
    'd0ebf10f-0469-4f04-a64e-2b28a5b24f76',
    '186ffeca-cd55-45ae-9f97-b2135a1845c4',
    '6f1cb1fb-54d2-4b07-86b1-4900df951d33',
    '72022401-d484-47e6-802b-e486381a9540',
    '1e2232f8-f4af-493e-9941-b12f51477eb9',
    '67f15da0-87ff-41a8-a804-047e9fe13176',
    'c3ce702d-133c-4eda-9952-db4cafab140d',
    'fb56a8f3-3f7b-45b2-a708-fd5cf422e8dc']

def get_uuid(index):
    """get a uuid, each index will be a new id.
    But always the same with each index"""
    return UUIDS[index]
