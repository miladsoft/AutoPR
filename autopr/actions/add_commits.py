from autopr.actions.base import Action, ContextDict
from autopr.actions.utils.commit import CommitPlan, PullRequestAmendment
from autopr.models.artifacts import Issue, PullRequest


class AddCommits(Action):
    id = "plan_commits"
    description = "Plan commits to add to the pull request."

    class Arguments(Action.Arguments):
        pull_request_amendment: PullRequestAmendment

        output_spec = f"""<list 
    name='planned_commits'
/>
<object>
{CommitPlan.output_spec}
</object>
</list>"""

    def run(self, arguments: Arguments, context: ContextDict) -> ContextDict:
        # Add the commits to the pull request
        context['pull_request_amendment'] = arguments.pull_request_amendment

        # If there is a comment, add it to the issue
        if arguments.pull_request_amendment.comment:
            self.publish_service.comment_on_issue(arguments.pull_request_amendment.comment)

        # Return the context
        return context
