from webargs import fields


def create_args():
    """Defines and validates params for create"""
    return {
        "id": fields.UUID(required=True, location='view_args'),
        "provider": fields.String(required=True),
        "id_token": fields.String(required=True)
    }


def update_args():
    """Defines and validates params for update"""
    return {
        "id": fields.UUID(required=True, location='view_args'),
        "provider": fields.String(required=True, location='view_args'),
        "auth_code": fields.String(required=True)
    }


def revoke_access_args():
    """Defines and validates params for revoke_access"""
    return {
        "id": fields.UUID(required=True, location='view_args'),
        "provider": fields.String(required=True, location='view_args')
    }
