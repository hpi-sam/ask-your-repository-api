from expects import expect, have_key, have_len, contain_only, equal, be, be_empty
from mamba import description, before, after, it
from neomodel import db

from application.models.user import User
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('/teams') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        pass

    with description('GET'):