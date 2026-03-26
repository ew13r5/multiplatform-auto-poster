class PostNotEditableError(Exception):
    """Raised when trying to edit a post that is published or failed."""
    def __init__(self, post_id: str, status: str):
        self.post_id = post_id
        self.status = status
        super().__init__(f"Post {post_id} has status '{status}', cannot edit")


class PageNotFoundError(Exception):
    """Raised when page_id does not exist."""
    def __init__(self, page_id: str):
        self.page_id = page_id
        super().__init__(f"Page {page_id} not found")


class InvalidFileError(Exception):
    """Raised for invalid file uploads."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)
