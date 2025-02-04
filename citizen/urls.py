from django.urls import path
from .views import *

urlpatterns = [
    path('citizen-dashboard', citizen_dashboard, name='citizen_dashboard'),
    path('citizen-header', header, name='header'),
    path('lawyers/', lawyers_list, name='lawyers_list'),
    path('file-cases', file_cases, name='file_cases'),
    path('my-cases', my_cases, name='my_cases'),
    path('against-cases', against_cases, name='against_cases'),
    path('citizen-hearings', hearings, name='citizen_hearings'),
    # path('citizen-efilling', citizen_efilling, name='citizen_efilling'),
    path('notifications', notifications, name='notifications'),
    path('documents', case_documents, name='case_documents'),
    path('citizen-notifications', notifications, name='citizen_notifications'),
    path('requested-payments', requested_payments, name='requested_payments'),
    path('create-order', create_order, name='create_order'),
    path('verify-payment', verify_payment, name='verify_payment'),
    path('citizen-profile', citizen_profile, name='citizen_profile'),
    path('citizen-edit-profile', citizen_edit_profile, name='citizen_edit_profile'),
    path('citizen-verdicts', citizen_verdicts, name='citizen_verdicts'),
    path('logout', logout_view, name='logout'),
    path('select_lawyer/', select_lawyer, name='select_lawyer'),
]
