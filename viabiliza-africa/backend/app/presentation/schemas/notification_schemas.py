from marshmallow import Schema, fields


class MarkChatReadSchema(Schema):
    message_id = fields.UUID(required=False, allow_none=True)


class PresenceHeartbeatSchema(Schema):
    pass
