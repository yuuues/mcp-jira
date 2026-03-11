"""MCP Tools/Services - Individual tool classes for each MCP function."""

from .base import MCPTool
from .get_issue import GetIssueService
from .search_issues import SearchIssuesService
from .get_transitions import GetTransitionsService
from .get_projects import GetProjectsService
from .get_myself import GetMyselfService
from .add_comment import AddCommentService
from .transition_issue import TransitionIssueService
from .assign_issue import AssignIssueService
from .create_issue import CreateIssueService
from .clone_issue import CloneIssueService
from .create_subtask import CreateSubtaskService
from .edit_issue import EditIssueService
from .get_attachments import GetAttachmentsService
from .download_attachment import DownloadAttachmentService
from .get_field_options import GetFieldOptionsService

ALL_TOOLS = [
    GetIssueService,
    SearchIssuesService,
    GetTransitionsService,
    GetProjectsService,
    GetMyselfService,
    AddCommentService,
    TransitionIssueService,
    AssignIssueService,
    CreateIssueService,
    CloneIssueService,
    CreateSubtaskService,
    EditIssueService,
    GetAttachmentsService,
    DownloadAttachmentService,
    GetFieldOptionsService,
]

__all__ = [
    'MCPTool',
    'GetIssueService',
    'SearchIssuesService',
    'GetTransitionsService',
    'GetProjectsService',
    'GetMyselfService',
    'AddCommentService',
    'TransitionIssueService',
    'AssignIssueService',
    'CreateIssueService',
    'CloneIssueService',
    'CreateSubtaskService',
    'EditIssueService',
    'GetAttachmentsService',
    'DownloadAttachmentService',
    'GetFieldOptionsService',
    'ALL_TOOLS',
]
