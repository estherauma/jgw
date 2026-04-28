from preference.models import OrganizationGroup


class OrganizationService:
    @staticmethod
    def create_organization_group(*, form, user):
        organization_group = form.save(commit=False)
        organization_group.created_by = user
        organization_group.updated_by = user
        organization_group.save()
        return organization_group

    @staticmethod
    def get_organization_group(*, organization_group_id):
        return (
            OrganizationGroup.objects.prefetch_related("organizations")
            .filter(id=organization_group_id)
            .first()
        )

    @staticmethod
    def build_organization_group_context(*, organization_group):
        return {
            "organization_group": organization_group,
            "organizations": organization_group.organizations.order_by("name"),
        }
