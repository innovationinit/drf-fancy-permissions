
from django.http.request import HttpRequest

from rest_framework.permissions import (
    BasePermission,
    DjangoModelPermissions,
)


class ActionPermissionMixin:

    def prepare_action(self, request, view):
        if view.action is None and isinstance(request, HttpRequest):
            # Action can be None if request wasn't initialized
            view.initialize_request(request)
        method = request.method.lower()
        if method == 'options':
            action = 'metadata'
        else:
            action = view.action_map.get(method, None)
        return action


def model_action_permission_factory(**action_permissions):
    class Perms(ActionPermissionMixin, DjangoModelPermissions):
        perms_map = action_permissions
        open_actions = ['metadata']
        perms_join = 'or'  # or 'and'

        def get_required_permissions(self, action, model_cls):
            """Given a model and an view action, return the list of permission codes that the user is required to have.

            Note: It uses action instead of method in parent class
            """
            return self.perms_map.get(action, [])

        def has_permission(self, request, view):
            """Return `True` if permission is granted, `False` otherwise"""
            action = self.prepare_action(request, view)

            if action in self.open_actions:
                return True  # authorization handled in the BaseApiView

            perms = self.get_required_permissions(action, model_cls=None)
            if not request.user or not (request.user.is_authenticated or not self.authenticated_users_only):
                return False

            if perms is None:
                return True

            if len(perms) == 0:
                return False

            if self.perms_join == 'and':
                return request.user.has_perms(perms)

            if self.perms_join == 'or':
                return any(request.user.has_perm(perm) for perm in perms)

            raise Exception('Unknown permission join method, should be one of `and` or `or`')

    return Perms


class ObjectPermissionMixin(ActionPermissionMixin):

    def check_object_permissions(self, request, view, obj):
        action = self.prepare_action(request, view)

        if action in self.open_actions:
            return True  # authorization handled in the BaseApiView

        if not request.user or not request.user.is_authenticated:
            return False

        perms_predicates = self.perms_map.get(action, [])
        if perms_predicates is None:
            return True

        if len(perms_predicates) == 0:
            return False

        if self.perms_join == 'and':
            return all(func(obj, request.user) for func in perms_predicates)

        if self.perms_join == 'or':
            return any(func(obj, request.user) for func in perms_predicates)

        raise Exception('Unknown permission join method, should be one of `and` or `or`')


def object_action_permission_factory(**action_permissions):
    class Perms(ObjectPermissionMixin, BasePermission):
        perms_map = action_permissions
        open_actions = ['metadata']
        perms_join = 'or'  # or 'and'

        def has_object_permission(self, request, view, obj):
            """Return `True` if permission is granted, `False` otherwise"""
            return self.check_object_permissions(request, view, obj)

    return Perms


def parent_object_action_permission_factory(**action_permissions):
    class Perms(ObjectPermissionMixin, BasePermission):
        perms_map = action_permissions
        open_actions = ['metadata']
        perms_join = 'or'  # or 'and'

        def has_permission(self, request, view):
            """Return `True` if permission is granted, `False` otherwise"""
            if hasattr(view, 'get_parent_object'):
                obj = view.get_parent_object()
            else:
                return True

            if not obj:
                return True

            return self.check_object_permissions(request, view, obj)

    return Perms
