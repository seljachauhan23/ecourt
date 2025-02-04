from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth import logout
from users.models import *  # Import all models from users app
from cases.models import *  # Ensure Document model is imported
from payment.models import *
from notifications.models import Notification  # Assuming there is a Notification model in the notifications app
import random
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from administrator.models import *
import razorpay
from django.views.decorators.csrf import csrf_exempt
import json 
import logging
from django.db.models import Q
import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.timezone import localtime

# Razorpay Client Setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

logger = logging.getLogger(__name__)

@login_required(login_url='/login/')
def citizen_dashboard(request):
    return render(request, 'citizen_dashboard.html')

@login_required(login_url='/login/')
def header(request):
    return render(request, 'citizen_header.html')

@login_required(login_url='/login/')
def lawyers_list(request):
    # Retrieve all lawyers from the database
    lawyers = Lawyer.objects.all()
    return render(request, 'registered_lawyers.html', {'lawyers': lawyers})

@login_required(login_url='/login/')
def file_cases(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    defendants = Citizen.objects.exclude(user=request.user)
    Users = User.objects.filter(user_type='LAWYER', is_active=1)
    Lawyers = Lawyer.objects.filter(user__in=Users)

    if request.method == 'POST':
        case_title = request.POST.get('case_title')
        case_type = request.POST.get('case_type')
        case_description = request.POST.get('case_description')
        defendant_name = request.POST.get('defendant')
        assigned_lawyer_name = request.POST.get('assigned_lawyer')
        case_documents = request.FILES.getlist('case_documents')

        try:
            defendant = User.objects.get(full_name=defendant_name).citizen
        except User.DoesNotExist:
            messages.error(request, 'Defendant not found.')
            return redirect('file_cases')

        assigned_lawyer = None
        if assigned_lawyer_name:
            try:
                assigned_lawyer = User.objects.get(full_name=assigned_lawyer_name).lawyer
            except User.DoesNotExist:
                messages.error(request, 'Assigned lawyer not found.')
                return redirect('file_cases')

        case_number = f"{case_type.upper()}-{random.randint(1000, 9999)}"

        case = Case.objects.create(
            case_number=case_number,
            plaintiff=request.user.citizen,
            defendant=defendant,
            assigned_lawyer=assigned_lawyer,
            case_title=case_title,
            case_type=case_type,
            case_description=case_description,
            status='PENDING'
        )

        citizen = Citizen.objects.get(user=request.user)

        for document in case_documents:
            Document.objects.create(
                case=case,
                document_type='Case Document',
                file=document,
                uploaded_by=request.user,
                user_type = 'citizen'
            )

        subject = f"Case Filed Successfully - {case.case_title}"
        message = f"""
        Dear {citizen.user.first_name},

        Your case has been successfully filed with the following details:

        Case Number: {case.case_number}
        Case Title: {case.case_title}
        Case Type: {case.case_type}
        Defendant: {case.defendant}
        Status: {case.status}

        You can log in to the eCourt portal to view more details and updates.

        Thank you,
        eCourt Team
            """
        recipient_email = request.user.email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )

        messages.success(request, 'Case filed successfully.')
        return redirect('my_cases')
    return render(request, 'file_case.html', {'defendants': defendants, 'Lawyers': Lawyers})

@login_required(login_url='/login/')
def my_cases(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True
    if request.GET.get('case_id'):
        if request.method == 'POST':
            lawyer_name = request.POST.get('assigned_lawyer')
            case_id = request.GET.get('case_id')
            try:
                plaintiff_lawyer = User.objects.get(full_name=lawyer_name)
                plaintiff_lawyer = Lawyer.objects.get(user=plaintiff_lawyer)
                case = Case.objects.get(id=case_id)
                if case.assigned_lawyer == plaintiff_lawyer:
                    error = 'this lawyer selected by plaintiff.'
                    return render(request, 'against_cases.html', {'error': error})
                case.assigned_lawyer = plaintiff_lawyer
                case.lawyer_accepted = None  # Reset the acceptance status
                case.save()
                messages.success(request, 'Lawyer selected successfully.')
            except Case.DoesNotExist:
                messages.error(request, 'Case not found.')
            except Lawyer.DoesNotExist:
                messages.error(request, 'Lawyer not found.')
            return redirect('my_cases')
    else:
        citizen = Citizen.objects.get(user=request.user)
        cases = Case.objects.filter(plaintiff=citizen)
        Users = User.objects.filter(user_type='LAWYER', is_active=1)
        Lawyers = Lawyer.objects.filter(user__in=Users)

    if request.method == 'POST':
        action = request.POST.get('action')
        case_id = request.POST.get('case_id')

        if action == 'upload_document':
            document_type = request.POST.get('document_type')
            file = request.FILES.get('file')
            case = Case.objects.get(id=case_id)

            Document.objects.create(
                case=case,
                document_type=document_type,
                file=file,
                uploaded_by=request.user,
                user_type='CITIZEN'
            )

            messages.success(request, 'Document uploaded successfully.')
            return redirect('my_cases')

    return render(request, 'my_cases.html', {'cases': cases, 'Lawyers': Lawyers})

@login_required(login_url='/login/')
def citizen_profile(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    user = request.user
    citizen = Citizen.objects.get(user=user)
    return render(request, 'citizen_profile.html', {'user': user, 'citizen': citizen})

@login_required(login_url='/login/')
def citizen_edit_profile(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    user = request.user
    citizen = Citizen.objects.get(user=user)

    if request.method == 'POST':
        user.email = request.POST['email']
        user.contact_number = request.POST['contact_number']
        user.address = request.POST['address']
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        
        if not user.email:
            messages.error(request, 'Email is required')
            return redirect('citizen_profile')
        else:
            try:
                validate_email(user.email)  # Validate email format
            except ValidationError:
                messages.error(request, 'Invalid email address')
                return redirect('citizen_profile')

        if not user.contact_number:
            messages.error(request, 'Phone number is required')
            return redirect('citizen_profile')
        
        elif not user.contact_number.isdigit() or len(user.contact_number) != 10:  # Adjust length as per requirement
            messages.error(request, 'Invalid phone number. It should be 10 digits long')
            return redirect('citizen_profile')

        if not user.address:
            messages.error(request, 'Address is required')
            return redirect('citizen_profile')

        # Proceed if all validations pass
        messages.success(request, 'Profile updated successfully!')


        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('citizen_profile')
    return render(request, 'citizen_edit_profile.html', {'user': user, 'citizen': citizen})


@login_required(login_url='/login/')
def case_documents(request):
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
    return render(request, 'my_case_docs.html', {'documents': documents})

@login_required(login_url='/login/')
def notifications(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.read = True
            notification.save()
            messages.success(request, 'Notification marked as read.')
        except Notification.DoesNotExist:
            messages.error(request, 'Notification not found.')

    notifications = Notification.objects.filter(user=request.user).order_by('-date_sent')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required(login_url='/login/')
def against_cases(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    if request.session.get('lawyer_selected') is not True:
        request.session['lawyer_selected'] = ''

    if request.method == 'POST':
        action = request.POST.get('action')
        case_id = request.POST.get('case_id')
            
        if action == 'select_lawyer':
            defendant_lawyer = request.POST.get('defendant_lawyer')
            try:
                defendant_lawyer = User.objects.get(full_name=defendant_lawyer)
                defendant_lawyer = Lawyer.objects.get(user=defendant_lawyer)
                case = Case.objects.get(id=case_id)
                if case.defendant_lawyer == defendant_lawyer:
                    error = 'this lawyer selected by defendant.'
                    return render(request, 'against_cases.html', {'error': error})
                case.defendant_lawyer = defendant_lawyer
                case.save()
                request.session['lawyer_selected'] = True
                messages.success(request, 'Lawyer assigned successfully.')
            except User.DoesNotExist:
                messages.error(request, 'Assigned lawyer not found.')
            return redirect('against_cases')
        
        if action == 'upload_document':
            document_type = request.POST.get('document_type')
            file = request.FILES.get('file')
            case = Case.objects.get(id=case_id)

            Document.objects.create(
                case=case,
                document_type=document_type,
                file=file,
                uploaded_by=request.user,
                user_type='CITIZEN'
            )

            messages.success(request, 'Document uploaded successfully.')
            # Check the current URL path and redirect accordingly
            return redirect('against_cases')

    citizen = Citizen.objects.get(user=request.user)

    # Step 1: Get all cases where the citizen is the defendant.
    cases = Case.objects.filter(defendant=citizen)

    lawyers = Lawyer.objects.all()

    return render(request, 'against_cases.html', {'cases': cases, 'Lawyers': lawyers})

@login_required(login_url='/login/')
def hearings(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    hearings = Hearing.objects.all()
    return render(request, 'citizen_hearings.html', {'hearings': hearings})

@login_required(login_url='/login/')
def logout_view(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def requested_payments(request):
    # Clear all previous messages
    messages.get_messages(request).used = True

    RAZORPAY_KEY_ID = getattr(settings, 'RAZORPAY_KEY_ID', None)
    if not RAZORPAY_KEY_ID:
        return HttpResponse("Razorpay Key ID is missing in the settings.", status=500)

    # Fetch the citizen object for the current user
    try:
        citizen = Citizen.objects.get(user=request.user)
    except Citizen.DoesNotExist:
        return HttpResponse("Citizen not found", status=404)

    # Fetch all cases where the citizen is a plaintiff or a defendant
    cases = Case.objects.filter(
        plaintiff=citizen) | Case.objects.filter(defendant=citizen)

    if cases.exists():
        try:
            payments = Payment.objects.filter(
                    citizen_email__iexact=request.user.email)
        except Payment.DoesNotExist:
            payments = []  # No payments found
    else:
        payments = []  # No cases found

    # Render the template
    context = {
        'RAZORPAY_KEY_ID': RAZORPAY_KEY_ID,
        'payments': payments,
        'message': 'No payments found.' if not payments else '',
    }
    return render(request, 'requested_payments.html', context)

def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        payment_id = data.get("payment_id")
        amount = data.get('amount')  # Amount in paise
        amount = float(amount) * 100
        amount = int(amount)  # Convert to integer
        currency = "INR"
        user_email = request.user.email  # Fetch email from the logged-in user

        try:
            order_info = {
                "amount": amount,
                "currency": currency,
                "payment_capture": 1  # Automatically capture payment
            }
            # Create the Razorpay order
            order = razorpay_client.order.create(order_info)
            order_id = order.get('id')
            if not order_id:
                logger.error(
                    "Failed to retrieve order_id from Razorpay response")
                return JsonResponse({'error': 'Failed to create Razorpay order. Try again.'}, status=500)
            else:
                # Save payment details to the database
                payment = Payment.objects.get(id=payment_id)
                payment.order_id = order_id
                payment.save()

            request.session['payment_id'] = payment_id
            print(order_id)
            
            return JsonResponse({'order_id': order_id, 'amount': amount, 'email': user_email})
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            return JsonResponse({'error': f'Error creating Razorpay order: {str(e)}'}, status=500)

    logger.error("Invalid request method for create_order")
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def verify_payment(request):
    if request.method == "POST":
        try:
            # Parse JSON payload
            data = json.loads(request.body)
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')

            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                return JsonResponse({'status': 'Failed', 'message': 'Invalid payment data'}, status=400)

            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                # Signature verification
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({'status': 'Failed', 'message': 'Payment verification failed. Invalid signature.'}, status=400)
            
            date_time = datetime.datetime.now()
            # Update payment status in the database
            try:
                payment = Payment.objects.get(order_id=razorpay_order_id)
                payment.payment_id = razorpay_payment_id
                payment.signature = razorpay_signature
                payment.status = 'Completed'
                payment.refund_amount = 0
                payment.citizen_email = request.user.email
                payment.paid_at = date_time
                payment.save()

            except Payment.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'Payment record not found'}, status=404)
            try:
                payment = Payment.objects.get(order_id=razorpay_order_id)

                # Check if the status is 'Completed'
                if payment.status != 'Completed':
                    payment.delete()  # Delete the payment if the status is not 'Completed'

            except:
                # Handle the case where no matching Payment record is found
                print("Payment record not found for the provided order_id.")

            payment = Payment.objects.get(order_id=razorpay_order_id)

            user = request.user

            subject = 'Payment Successful'
            message = f"""
            Dear {user.username},

            We are pleased to inform you that your payment has been successfully processed.

            Payment Details:
            - Case Number = {payment.case.case_number}
            - Amount Paid: ₹{payment.amount:.2f}
            - Payment ID: {payment.payment_id}
            - Paid At: {localtime(payment.paid_at)}

            Thank you for using our services. If you have any questions, feel free to contact us.

            Best regards,
            eCourt Team
            """
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return JsonResponse({'status': 'success', 'message': 'Payment Verified'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'Failed', 'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'status': 'Failed', 'message': 'Invalid request method'}, status=400)

@login_required(login_url='/login/')
def citizen_verdicts(request):
    user = request.user
    verdicts = Case.objects.filter(Q(plaintiff__user=user) | Q(defendant__user=user), status='CLOSED')
    return render(request, 'citizen_verdicts.html', {'verdicts': verdicts})

def select_lawyer(request):
    case_id = request.session.get('case_id')
    if request.method == 'POST':
        lawyer_name = request.POST.get('assigned_lawyer')
        try:
            case = Case.objects.get(id=case_id)
            lawyer = Lawyer.objects.get(user__full_name=lawyer_name)
            case.assigned_lawyer = lawyer
            case.lawyer_accepted = None  # Reset the acceptance status
            case.save()
            messages.success(request, 'Lawyer selected successfully.')
        except Case.DoesNotExist:
            messages.error(request, 'Case not found.')
        except Lawyer.DoesNotExist:
            messages.error(request, 'Lawyer not found.')
        return redirect('my_cases')
    return redirect('my_cases')