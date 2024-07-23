from django.shortcuts import render
from django.utils.timezone import now, timedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import CommandLog

def pipeline_status(request):
    two_weeks_ago = now() - timedelta(days=30)
    logs = CommandLog.objects.filter(executed_at__gte=two_weeks_ago).order_by('-executed_at')
    logs_count =len(logs)
    successful_count = logs.filter(command_status=True).count()

    failed_count = logs.filter(command_status=False).count()

    paginator = Paginator(logs, 15)  
    page = request.GET.get('page')
    
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)
    
    context = {
        'logs': logs,
        'logsCount': logs_count,
        'successfulCount': successful_count,
        'failedCount': failed_count,
    }
    
    return render(request, 'pipeline/pipeline_status.html', context)

