from django.urls import path
from .views import *

urlpatterns = [
   path('judge-dashboard', judge_dashboard, name='judge_dashboard'),
   path('judge-assigned-cases', judge_assigned_cases, name='judge_assigned_cases'),
   path('update-case-status/', update_case_status, name='update_case_status'),
   path('judge-hearings', judge_hearings, name='judge_hearings'),
   path('hearing-videocall-url/', hearing_videocall_url,
        name='submit_videocall_url'),
    path('hearing-outcome/', submit_hearing_outcome, name='submit_hearing_outcome'),
   # path('outcome', outcome, name='outcome'),
   path('case-docs', case_docs, name='case_docs'),
   path('judge-profile', judge_profile, name='judge_profile'),
   path('judge-edit-profile', judge_edit_profile, name='judge_edit_profile'),
   path('logout', logout_view, name='logout'),
   path('schedule-hearing', schedule_hearing, name='schedule_hearing'),
   path('judge-notifications', judge_notifications, name='judge_notifications'),
   path('verdicts', verdicts, name='verdicts'),
   path('final-outcome', final_outcome, name='final_outcome'),
]