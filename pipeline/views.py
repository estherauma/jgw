from django.shortcuts import render
from django.utils.timezone import now, timedelta
from .models import CommandLog

def pipeline_status(request):
    two_weeks_ago = now() - timedelta(days=30)
    logs = CommandLog.objects.filter(executed_at__gte=two_weeks_ago).order_by('-executed_at')
    logs_count =len(logs)
    successful_count = logs.filter(command_status=True).count()

    failed_count = logs.filter(command_status=False).count()
    
    context = {
        'logs': logs,
        'logsCount': logs_count,
        'successfulCount': successful_count,
        'failedCount': failed_count,
    }
    
    return render(request, 'pipeline/pipeline_status.html', context)

