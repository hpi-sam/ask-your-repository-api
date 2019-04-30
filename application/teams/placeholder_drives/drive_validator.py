from webargs import fields


def create_args():
    """Defines and validates params for create"""
    return {"drive_id": fields.String(required=True), "team_id": fields.UUID(required=True, location="view_args")}


def delete_args():
    """Defines and validates a request for Drive deletion"""
    return {
        "drive_id": fields.UUID(required=True, location="view_args"),
        "teams_id": fields.UUID(required=True, location="view_args"),
    }
