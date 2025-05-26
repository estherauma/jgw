from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from other_resource.forms import EditResourceForm
from .models import OtherResource
from django.contrib.auth.models import Group
from users.utils import get_user_group

@login_required
def other_resource_view(request):
    user=request.user
    user_group=get_user_group(user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        link = request.POST.get('link')
        group_id = request.POST.get('group')

        group = Group.objects.get(id=group_id) if group_id else None

        OtherResource.objects.create(
            title=title,
            description=description,
            link=link,
            group=group,
        )
        return redirect('other_resource:other_resource') 

    groups = Group.objects.all()
    if user.is_superuser:
        resources = OtherResource.objects.all()
    else:
        resources = OtherResource.objects.filter(group__name__in=user_group)
    return render(request, 'other_resource.html', {'groups': groups, 'resources': resources})

@login_required
def edit_resource(request, resource_id):
    resource = get_object_or_404(OtherResource, pk=resource_id)
    groups = Group.objects.all()

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
        'groups': groups,
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
