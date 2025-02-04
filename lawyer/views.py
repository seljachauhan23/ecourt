from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth import logout
from django.core.mail import send_mail
import random
from users.models import *  # Import all models from users app
from cases.models import *  # Assuming there is a Case model in the cases app
from payment.models import *
from notifications.models import Notification
from administrator.models import * # Assuming there is
from django.db.models import Q
import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

@login_required(login_url='/login/')
def lawyer_dashboard(request):
    return render(request, 'lawyer_dashboard.html')

def header(request):
    return render(request,'lawyer_header.html')

@login_required(login_url='/login/')
def assigned_cases(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    lawyer = Lawyer.objects.get(user=request.user)
    plaintiff_cases = Case.objects.filter(assigned_lawyer=lawyer, lawyer_accepted=True)
    defendant_cases = Case.objects.filter(
        defendant_lawyer=lawyer, defendant_lawyer_accepted=True)
    cases = plaintiff_cases | defendant_cases
    cases = cases.distinct()
    return render(request, 'assigned_cases.html', {'cases': cases})

@login_required(login_url='/login/')
def hearings(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    hearings = Hearing.objects.all()
    return render(request, 'lawyer_hearings.html', {'hearings': hearings})

@login_required(login_url='/login/')
def lawyer_upload_document(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    lawyer = Lawyer.objects.get(user=request.user)
    cases = Case.objects.filter(assigned_lawyer=lawyer)

    if request.method == 'POST':
        case_id = request.POST.get('case_id')
        document_type = request.POST.get('document_type')
        file = request.FILES.get('file')
        case = Case.objects.get(id=case_id)     
        Document.objects.create(
            case=case,
            document_type=document_type,
            file=file,
            uploaded_by=request.user,
            user_type='LAWYER'
        )

        messages.success(request, 'Document uploaded successfully.')
        return redirect('assigned_cases')
    return render(request, 'assigned_cases.html', {'cases': cases})

@login_required(login_url='/login/')
def lawyer_profile(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    lawyer = Lawyer.objects.get(user=request.user)
    user = User.objects.get(id=lawyer.user.id)
    return render(request, 'lawyer_profile.html', {'lawyer': lawyer, 'user': user})

@login_required(login_url='/login/')
def lawyer_edit_profile(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    lawyer = Lawyer.objects.get(user=request.user)
    user = User.objects.get(id=lawyer.user.id)
    if request.method == 'POST':
        email = request.POST.get('email', user.email)
        phone = request.POST.get('phone', lawyer.user.contact_number)
        license_number = request.POST.get('license_number', lawyer.license_number)
        law_firm = request.POST.get('law_firm', lawyer.law_firm)
        
        # Add validations
        if not email:
            messages.error(request, 'Email is required')
            return redirect('lawyer_profile')
        else:
            try:
                validate_email(email)  # Validate email format
            except ValidationError:
                messages.error(request, 'Invalid email address')
                return redirect('lawyer_edit_profile')

        if not phone:
            messages.error(request, 'Phone number is required')
            return redirect('lawyer_edit_profile')
        elif not phone.isdigit() or len(phone) != 10:  # Adjust length as per requirement
            messages.error(request, 'Invalid phone number. It should be 10 digits long')
            return redirect('lawyer_edit_profile')

        if not license_number:
            messages.error(request, 'License number is required')
            return redirect('lawyer_edit_profile')

        if not law_firm:
            messages.error(request, 'Law firm is required')
            return redirect('lawyer_edit_profile')
        
        user.email = email
        user.contact_number = phone
        lawyer.license_number = license_number
        lawyer.law_firm = law_firm
        
        # Add other fields as necessary
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        lawyer.save()
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('lawyer_profile')
    else:
        return HttpResponseBadRequest("Invalid request method")

@login_required(login_url='/login/')
def lawyer_profile(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    user = request.user
    lawyer = Lawyer.objects.get(user=user)
    return render(request, 'lawyer_profile.html', {'user': user, 'lawyer': lawyer})

@login_required(login_url='/login/')
def lawyer_edit_profile(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    user = request.user
    if request.method == 'POST':
        user.username = user.username
        user.full_name = request.POST['full_name']
        user.email = request.POST['email']
        user.contact_number = request.POST['contact_number']
        user.address = request.POST['address']
        if request.FILES.get('profile_image'):
            user.profile_picture = request.FILES['profile_image']

        # Add validations
        if not user.full_name:
            messages.error(request, 'Name is required')
            return redirect('lawyer_profile')
        if not user.email:
            messages.error(request, 'Email is required')
            return redirect('lawyer_profile')
        if not user.contact_number:
            messages.error(request, 'Phone number is required')
            return redirect('lawyer_profile')
        if not user.address:
            messages.error(request, 'addrress is required')
            return redirect('lawyer_profile')

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('lawyer_profile')
    return render(request, 'lawyer_edit_profile.html', {'user': user})

@login_required(login_url='/login/')
def logout_view(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required(login_url='/login/')
def plaintiff_case_requests(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    lawyer = Lawyer.objects.get(user=request.user)
    plantiff_cases = Case.objects.filter(assigned_lawyer=lawyer, lawyer_accepted=None)

    cases = plantiff_cases

    return render(request, 'plaintiff_case_requests.html', {'cases': cases})


@login_required(login_url='/login/')
def plaintiff_accept_case(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    case_id = request.GET.get('case_id')
    case = Case.objects.get(id=case_id)
    case.lawyer_accepted = True
    case.status = 'PENDING'
    case.save()

    case_id = request.GET.get('case_id')
    case = Case.objects.get(id=case_id)
    if case.lawyer_accepted == True and case.defendant_lawyer_accepted == True:
        judge = random.choice(Judge.objects.all())
        case.assigned_judge = judge
        case.save()

    # Send email to the plaintiff
    send_mail(
        'Case Accepted',
        f'Your case {case.case_number} has been accepted by the lawyer.',
        'ecourtofficially@gmail.com',
        [case.plaintiff.user.email],
        fail_silently=False,
    )

    # Send email to the defendant
    send_mail(
        'Case Accepted by Plaintiff\'s Lawyer',
        f'The case {case.case_number} has been accepted by the plaintiff\'s lawyer.',
        'ecourtofficially@gmail.com',
        [case.defendant.user.email],
        fail_silently=False,
    )

    messages.success(request, 'Case accepted successfully.')
    return redirect('plaintiff_case_requests')

@login_required(login_url='/login/')
def plaintiff_decline_case(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    case_id = request.GET.get('case_id')
    case = Case.objects.get(id=case_id)


    if case.assigned_lawyer:
        case.assigned_lawyer = None
        case.lawyer_accepted = False
    
    if case.defendant_lawyer:
        case.defendant_lawyer = None
        case.defendant_lawyer_accepted = False

    case.save()

    send_mail(
        'Case Declined',
        f'Your case {case.case_number} has been declined by the lawyer.',
        'ecourtofficially@gmail.com',
        [case.plaintiff.user.email],
        fail_silently=False,
    )

    messages.success(request, 'Case declined successfully.')
    return redirect('plaintiff_case_requests')


@login_required(login_url='/login/')
def defendant_case_requests(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    lawyer = Lawyer.objects.get(user=request.user)
    
    defendant_cases = Case.objects.filter(
        defendant_lawyer=lawyer, defendant_lawyer_accepted=None)
    cases = defendant_cases

    return render(request, 'defendant_case_requests.html', {'cases': cases})


@login_required(login_url='/login/')
def defendant_accept_case(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    case_id = request.GET.get('case_id')
    case = Case.objects.get(id=case_id)
    case.defendant_lawyer_accepted = True
    case.status = 'PENDING'
    case.save()

    case_id = request.GET.get('case_id')
    case = Case.objects.get(id=case_id)
    if case.lawyer_accepted == True and case.defendant_lawyer_accepted == True:
        judge = random.choice(Judge.objects.all())
        case.assigned_judge = judge
        case.save()


    send_mail(
        'Case Accepted',
        f'Your case {case.case_number} has been accepted by the lawyer.',
        'ecourtofficially@gmail.com',
        [case.defendant.user.email],
        fail_silently=False,
    )
    messages.success(request, 'Case accepted successfully.')
    return redirect('defendant_case_requests')


@login_required(login_url='/login/')
def defendant_decline_case(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    case_id = request.GET.get('case_id')
    case = Case.objects.get(id=case_id)

    send_mail(
        'Case Declined',
        f'Your case {case.case_number} has been declined by the lawyer.',
        'ecourtofficially@gmail.com',
        [case.defendant.user.email],
        fail_silently=False,
    )

    if case.defendant_lawyer:
        case.defendant_lawyer = None
    case.save()

    messages.success(request, 'Case declined successfully.')
    return redirect('defendant_case_requests')

@login_required(login_url='/login/')
def lawyer_notifications(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(
                id=notification_id, user=request.user)
            notification.read = True
            notification.save()
            messages.success(request, 'Notification marked as read.')
        except Notification.DoesNotExist:
            messages.error(request, 'Notification not found.')

    notifications = Notification.objects.filter(user=request.user).order_by('-date_sent')
    return render(request, 'lawyer_notifications.html', {'notifications': notifications})

@login_required(login_url='/login/')
def client_case_documents(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    case_id = request.GET.get('case_id')
    if not case_id:
        return HttpResponseBadRequest("Case ID is required")

    try:
        case = Case.objects.get(id=case_id)
        request.session['case_number'] = case.case_number
    except Case.DoesNotExist:
        return HttpResponseBadRequest("Invalid Case ID")

    documents = Document.objects.filter(case=case)
    return render(request, 'client_case_docs.html', {'documents': documents})


def request_client_case_documents(request):
    pass

@login_required(login_url='/login/')
def logout_view(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def request_payment(request, case_id):
    # Fetch the lawyer object for the current user
    try:
        lawyer = Lawyer.objects.get(user=request.user)
        if lawyer.bank_name is None or lawyer.bank_account_number is None or lawyer.ifsc_code is None and lawyer.branch_name is None or lawyer.bank_name == '' or lawyer.bank_account_number == '' or lawyer.ifsc_code == '' and lawyer.branch_name == '':
            return redirect('lawyer_bank_details')
    except Lawyer.DoesNotExist:
        lawyer = None  # Handle the absence of a lawyer

    if lawyer:
        # Try to fetch the cases where the lawyer is involved
        try:
            plaintiff_case = Case.objects.get(id=case_id, assigned_lawyer=lawyer)
        except Case.DoesNotExist:
            plaintiff_case = None  # Handle the absence of a plaintiff case

        try:
            defendant_case = Case.objects.get(id=case_id, defendant_lawyer=lawyer)
        except Case.DoesNotExist:
            defendant_case = None  # Handle the absence of a defendant case

        # Combine the cases if they exist
        if plaintiff_case and defendant_case:
            cases = plaintiff_case | defendant_case  # Combine the cases
        elif plaintiff_case:
            cases = plaintiff_case
        elif defendant_case:
            cases = defendant_case
        else:
            cases = 'no cases avaiable'  # No cases found

    else:
        cases = 'no lawyers avaiable'  # No lawyer found

    if plaintiff_case:
        if request.method == 'POST':
            amount = request.POST.get('amount')
            # Ensure that amount is a float
            try:
                amount = float(amount)
            except ValueError:
                amount = 0.0  # Set to 0 if conversion fails, or handle it appropriately
            description = request.POST.get('description')
            date_time = datetime.datetime.now()
            Payment.objects.create(case=plaintiff_case, lawyer_email=request.user.email, citizen_email = plaintiff_case.plaintiff.user.email,
                                   amount=amount, description=description, requested_at=date_time)
            Notification.objects.create(
                user=plaintiff_case.plaintiff.user,
                message=f'You have a new payment request for case {plaintiff_case.case_number}.'
            )
            
            # Send the email with all the payment details embedded
            send_mail(
                subject='Payment Request Details',
                message=f"""
            Hello {plaintiff_case.plaintiff.user.full_name},

            You have received a new payment request for the following case:

            - Case Number: {plaintiff_case.case_number}
            - Case Title: {plaintiff_case.case_title}
            - Requested Amount: ₹{amount:.2f}
            - Description: {description}
            - Requested At: {date_time}

            Please log in to your account on eCourt to review the request and make the payment if necessary.

            Login to your account and navigate to the "Requested Payments" section to complete this process.

            Thank you for your prompt attention.

            Best regards,
            eCourt Team
            """,
                from_email='ecourtofficially@gmail.com',
                recipient_list=[plaintiff_case.plaintiff.user.email],
                fail_silently=False,
            )
            return redirect('lawyer_payments')
    else:
        if defendant_case:
            if request.method == 'POST':
                amount = request.POST.get('amount')
                # Ensure that amount is a float
                try:
                    amount = float(amount)
                except ValueError:
                    amount = 0.0  # Set to 0 if conversion fails, or handle it appropriately
                description = request.POST.get('description')
                request_date_time = request.POST.get('current_datetime')
                date_time = datetime.datetime.now()
                Payment.objects.create(case=defendant_case, lawyer_email=request.user.email, citizen_email=defendant_case.defendant.user.email,
                                       amount=amount, description=description, requested_at=date_time)

                Notification.objects.create(
                user=defendant_case.defendant.user,
                message=f'You have a new payment request for case {defendant_case.case_number}.'
            )
                            # Send the email with all the content embedded
                send_mail(
                    subject='New Payment Request Notification',
                    message=f"""
                Hello {defendant_case.defendant.user.full_name},

                You have received a new payment request for the following case:

                - Case Number: {defendant_case.case_number}
                - Case Title: {defendant_case.case_title}
                - Requested Amount: ₹{amount:.2f}
                - Description: {description}
                - Requested At: {date_time}

                Please log in to your account on eCourt to review the request and make the payment if necessary.

                Login to your account and navigate to the "Requested Payments" section to complete this process.
    
                Thank you for your prompt attention.
    
                Best regards,
                eCourt Team
                """,
                    from_email='ecourtofficially@gmail.com',
                    recipient_list=[defendant_case.defendant.user.email],
                    fail_silently=False,
                )
                return redirect('lawyer_payments')
    return render(request, 'request_payment.html', {'case': cases})

@login_required(login_url='/login/')
def lawyer_payments(request):
    payments = Payment.objects.filter(lawyer_email=request.user.email)
    return render(request, 'lawyer_payments.html', {'payments': payments})

@login_required(login_url='/login/')
def lawyer_verdicts(request):
    lawyer = Lawyer.objects.get(user=request.user)
    plaintiff_cases = Case.objects.filter(assigned_lawyer=lawyer, status='CLOSED')
    defendant_cases = Case.objects.filter(
        defendant_lawyer=lawyer, status='CLOSED')
    verdicts = plaintiff_cases | defendant_cases
    return render(request, 'lawyer_verdicts.html', {'verdicts': verdicts})

@login_required(login_url='/login/')
def lawyer_bank_details(request):
    lawyer = Lawyer.objects.get(user=request.user)
    if request.method == 'POST':
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')
        branch_name = request.POST.get('branch_name')

        # Add validations
        if not bank_name:
            messages.error(request, 'Bank name is required')
            return redirect('lawyer_bank_details')
        if not account_number:
            messages.error(request, 'Account number is required')
            return redirect('lawyer_bank_details')
        if not ifsc_code:
            messages.error(request, 'IFSC code is required')
            return redirect('lawyer_bank_details')
        if not branch_name:
            messages.error(request, 'Branch name is required')
            return redirect('lawyer_bank_details')

        if not account_number.isdigit():
            messages.error(request, 'Account number should contain only digits')
            return redirect('lawyer_bank_details')

        if not re.match(r'^[A-Za-z]{4}\d{7}$', ifsc_code):
            messages.error(request, 'Invalid IFSC code format')
            return redirect('lawyer_bank_details')

        lawyer.bank_name = bank_name
        lawyer.bank_account_number = account_number
        lawyer.ifsc_code = ifsc_code
        lawyer.branch_name = branch_name
        lawyer.save()

        messages.success(request, 'Bank details updated successfully')
        return redirect('lawyer_bank_details')

    return render(request, 'lawyer_bank_details.html', {'lawyer': lawyer})
