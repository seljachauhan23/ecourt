from django.urls import path
from .views import *

urlpatterns = [
    path('admin-dashboard', admin_dashboard, name='admin_dashboard'),
    path('admin-header', header, name='header'),
    path('citizens-management', citizens_management, name='citizens_management'),
    path('lawyers-management', lawyers_management, name='lawyers_management'),
    path('judges-management', judges_management, name='judges_management'),
    path('case-management', case_management, name='case_management'),
    path('case-status', case_status, name='case_status'),
    path('pending-cases', pending_cases, name='pending_cases'),
    path('active-cases', active_cases, name='active_cases'),
    path('closed-cases', closed_cases, name='closed_cases'),
    path('dismissed-cases', dismissed_cases, name='dismissed_cases'),
    path('add-judge', add_judge, name='add_judge'),
    path('lawyer-approve-reject', lawyer_approve_reject, name='lawyer_approve_reject'),
    path('lawyer-approve', lawyer_approve, name='lawyer_approve'),
    path('lawyer-reject', lawyer_reject, name='lawyer_reject'),
    path('profile', profile, name='profile'),
    path('edit-profile', edit_profile, name='edit_profile'),
    path('logout', logout_view, name='logout'),
    path('analytics-dashboard', analytics_dashboard, name='analytics_dashboard'),
    path('reports-dashboard', reports_dashboard, name='reports_dashboard'),
    path('contact-us-reply', contact_us_reply, name='contact_us_reply'),
    path('view-payments', view_payments, name='view_payments'),
    path('proceed-payment/<int:payment_id>/', proceed_payment, name='proceed_payment'),
]

handler404 = 'ecourt_home.views.error_404_view'