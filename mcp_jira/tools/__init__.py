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

ALL_TOOLS = [
    GetIssueService,
    SearchIssuesService,
    GetTransitionsService,
    GetProjectsService,
    GetMyselfService,
    AddCommentService,
    TransitionIssueService,
    AssignIssueService,
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
    'ALL_TOOLS',
]
