class DomainError(Exception):
    code: str = "domain_error"


class NotFoundError(DomainError):
    code = "not_found"


class UserNotFoundError(NotFoundError):
    code = "user_not_found"

    def __init__(self, user_id: str):
        super().__init__(f"User '{user_id}' not found")


class ConversationNotFoundError(NotFoundError):
    code = "conversation_not_found"

    def __init__(self, conversation_id: str):
        super().__init__(f"Conversation '{conversation_id}' not found")


class ValidationError(DomainError):
    code = "validation_error"


class EmptyMessageError(ValidationError):
    code = "empty_message"

    def __init__(self):
        super().__init__("Message text must not be empty")


class InvalidParticipantsError(ValidationError):
    code = "invalid_participants"


class InvalidSearchQueryError(ValidationError):
    code = "invalid_search_query"

    def __init__(self):
        super().__init__("Search query must be at least 2 characters")


class ConflictError(DomainError):
    code = "conflict"


class UserNameTakenError(ConflictError):
    code = "user_name_taken"

    def __init__(self, name: str):
        super().__init__(f"User name '{name}' is already taken")


class DirectConversationExistsError(ConflictError):
    code = "direct_conversation_exists"

    def __init__(self, existing_id: str):
        self.existing_id = existing_id
        super().__init__(
            f"A direct conversation between these users already exists: {existing_id}"
        )


class ForbiddenError(DomainError):
    code = "forbidden"


class NotAParticipantError(ForbiddenError):
    code = "not_a_participant"

    def __init__(self):
        super().__init__("Sender is not a participant of this conversation")
