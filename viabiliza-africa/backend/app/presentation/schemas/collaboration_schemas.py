from marshmallow import Schema, fields, validate

from app.domain.enums.task_status import TaskStatus


class CreateTaskSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False, allow_none=True)
    assignee_id = fields.UUID(required=False, allow_none=True)
    due_date = fields.Date(required=False, allow_none=True)


class UpdateTaskSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False, allow_none=True)
    assignee_id = fields.UUID(required=False, allow_none=True)
    due_date = fields.Date(required=False, allow_none=True)


class MoveTaskSchema(Schema):
    status = fields.String(
        required=True,
        validate=validate.OneOf(TaskStatus.values()),
    )
    position = fields.Integer(required=False, validate=validate.Range(min=0))


class CreateTaskDependencySchema(Schema):
    predecessor_task_id = fields.UUID(required=True)
    successor_task_id = fields.UUID(required=True)


class SendChatMessageSchema(Schema):
    content = fields.String(
        required=True,
        validate=validate.Length(min=1, max=5000),
    )
