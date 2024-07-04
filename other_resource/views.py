from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from other_resource.forms import EditResourceForm, OtherResourceForm
from .models import OtherResource
from users.utils import get_user_organisations

@login_required
def other_resource_view(request):
    user = request.user
    user_organisations = get_user_organisations(user)
    if request.method == 'POST':
        if 'delete_resource_id' in request.POST:
            resource_id = request.POST.get('delete_resource_id')
            resource = get_object_or_404(OtherResource, pk=resource_id)
            resource.delete()
            return redirect('other_resource:other_resource')

        form = OtherResourceForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            return redirect('other_resource:other_resource')
    else:
        form = OtherResourceForm(user=user)

    resources = OtherResource.objects.filter(organisation__in=user_organisations)
    context = {
        'form': form,
        'resources': resources,
        'organisations': user_organisations,
    }
    return render(request, 'other_resource.html', context)

@login_required
def edit_resource(request, resource_id):
    resource = get_object_or_404(OtherResource, pk=resource_id)

    if request.method == 'POST':
        form = EditResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            return redirect('other_resource:other_resource')
    else:
        form = EditResourceForm(instance=resource)

    context = {
        'form': form,
        'resource': resource,
        'organisations': get_user_organisations(request.user),
    }

    return render(request, 'edit_resource.html', context)

@login_required
def delete_resource(request, resource_id):
    resource = get_object_or_404(OtherResource, pk=resource_id)
    if request.method == 'POST':
        resource.delete()
        if request.is_ajax():
            return JsonResponse({'deleted': True})
        return redirect('other_resource:other_resource')
    
    context = {
        'resource': resource,
    }

    return render(request, 'other_resource.html', context)
