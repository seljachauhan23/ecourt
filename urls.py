from django.contrib import admin
from django.urls import path
from administrator import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('header/', admin_views.header, name='header'),
    path('user_management/', admin_views.user_management, name='user_management'),
    path('citizens_management/', admin_views.citizens_management, name='citizens_management'),
    path('lawyers_management/', admin_views.lawyers_management, name='lawyers_management'),
    path('judges_management/', admin_views.judges_management, name='judges_management'),
    path('case_management/', admin_views.case_management, name='case_management'),
    path('case_status/', admin_views.case_status, name='case_status'),
    path('all_cases/', admin_views.all_cases, name='all_cases'),
    path('pending_cases/', admin_views.pending_cases, name='pending_cases'),
    path('active_cases/', admin_views.active_cases, name='active_cases'),
    path('closed_cases/', admin_views.closed_cases, name='closed_cases'),
    path('dismissed_cases/', admin_views.dismissed_cases, name='dismissed_cases'),
    path('add_judge/', admin_views.add_judge, name='add_judge'),
    path('lawyer_approve_reject/', admin_views.lawyer_approve_reject, name='lawyer_approve_reject'),
    path('approve_or_reject_lawyer/<str:username>/', admin_views.approve_or_reject_lawyer, name='approve_or_reject_lawyer'),
    path('profile/', admin_views.profile, name='profile'),
    path('edit_profile/', admin_views.edit_profile, name='edit_profile'),
    path('logout/', admin_views.logout_view, name='logout'),
    path('analytics_dashboard/', admin_views.analytics_dashboard, name='analytics_dashboard'),
    path('reports_dashboard/', admin_views.reports_dashboard, name='reports_dashboard'),
]
