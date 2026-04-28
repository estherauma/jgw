from preference.models import OrganizationGroup


class OrganizationService:
    @staticmethod
    def create_organization_group(*, form, user):
        organization_group = form.save(commit=False)
        organization_group.created_by = user
        organization_group.updated_by = user
        organization_group.save()
        return organization_group
