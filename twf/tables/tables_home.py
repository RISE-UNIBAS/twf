"""Table classes for displaying user permissions."""
import django_tables2 as tables

from twf.models import Project
from twf.permissions import get_available_actions


class UserPermissionTable(tables.Table):
    """Table for user permissions."""

    permission = tables.Column(accessor="permission", verbose_name="Permission")

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project', None)
        if not project_id:
            raise ValueError("project must be set.")

        # Get project and users
        self.project = Project.objects.get(id=int(project_id))
        users = [self.project.owner] + list(self.project.members.all())

        # Dynamically define user columns
        extra_columns = {
            profile.user.username: tables.Column(verbose_name=profile.user.username)
            for profile in users
        }

        # Create a dynamically built table class
        cls = type(
            'DynamicUserPermissionTable',
            (UserPermissionTable,),
            extra_columns
        )

        # Replace the class dynamically
        self.__class__ = cls

        # Explicitly pass the data using kwargs
        table_data = self.get_table_data(users)
        super().__init__(data=table_data, *args, **kwargs)

    def get_table_data(self, users):
        """Generate table rows for permissions."""
        actions = get_available_actions()

        # Build rows for the table
        table_data = []
        for action_name, action_details in actions.items():
            row = {
                "permission": action_details["label"],  # The action label
            }

            # Add user-specific data (e.g., True/False for each user's permission)
            for profile in users:
                row[profile.user.username] = self.user_has_permission(profile.user, action_name)

            table_data.append(row)

        return table_data

    def user_has_permission(self, user, action_name):
        """Check if a user has a specific permission. Replace with your logic."""
        return True  # Replace with actual logic for checking permissions
