from webargs import fields


def create_args():
    """Defines and validates params for create"""
    return {"folder_id": fields.String(required=True),
            "team_id": fields.UUID(required=True, location='view_args')}
