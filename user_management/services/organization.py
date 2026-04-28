from preference.models import Brand


class OrganizationService:
    @staticmethod
    def create_brand(*, form, user):
        brand = form.save(commit=False)
        brand.created_by = user
        brand.updated_by = user
        brand.save()
        return brand
