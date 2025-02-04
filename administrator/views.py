from django.shortcuts import render, redirect, get_object_or_404
from users.models import *
from cases.models import *
from .models import *
from payment.models import *
from .models import ContactUs
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json
from django.db.models import Count, F
from io import BytesIO
from django.db.models.functions import TruncMonth
from django.utils import timezone
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Create your views here.
@login_required(login_url='/login/')
def admin_dashboard(request):
    # Fetch some data to display on the dashboard
    total_cases = Case.objects.count()
    total_users = User.objects.count()
    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'total_cases': total_cases,
    })

@login_required(login_url='/login/')
def header(request):
    return render(request, 'admin_header.html')

@login_required(login_url='/login/')
def citizens_management(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        citizen = get_object_or_404(Citizen, id=user_id)
        reason = request.POST.get('reason')
        user = citizen.user
        citizen.delete()
        user.email_user(
            'Account Deletion Notification',
            f'Your account has been deleted for the following reason: {reason}',
            'ecourtofficially@gmail.com'
        )
        messages.success(request, 'Citizen deleted successfully.')
        return redirect('citizens_management')

    citizens = Citizen.objects.all()
    return render(request, 'citizens_management.html', {'citizens': citizens})

@login_required(login_url='/login/')
def lawyers_management(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        reason = request.POST.get('reason')
        lawyer = get_object_or_404(Lawyer, id=user_id)
        user = lawyer.user
        lawyer.delete()
        user.email_user(
            'Account Deletion Notification',
            f'Your account has been deleted for the following reason: {reason}',
            'ecourtofficially@gmail.com'
        )
        messages.success(request, 'Lawyer deleted successfully.')
        return redirect('lawyers_management')

    lawyers = Lawyer.objects.all()
    return render(request, 'lawyers_management.html', {'lawyers': lawyers})

@login_required(login_url='/login/')
def judges_management(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        reason = request.POST.get('reason')
        judge = get_object_or_404(Judge, id=user_id)
        user = judge.user
        judge.delete()
        user.email_user(
            'Account Deletion Notification',
            f'Your account has been deleted for the following reason: {reason}',
            'ecourtofficially@gmail.com'
        )
        messages.success(request, 'Judge deleted successfully.')
        return redirect('judges_management')

    judges = Judge.objects.all()
    return render(request, 'judges_management.html', {'judges': judges})

@login_required(login_url='/login/')
def case_management(request):
    if request.method == 'POST':
        print(request.POST)
        case_id = request.POST.get('case_id')
        reason = request.POST.get('reason')
        case = get_object_or_404(Case, id=case_id)
        case.delete()
        # Assuming the case has a related user to notify
        plaintiff_email = case.plaintiff.user.email
        defendant_email = case.defendant.user.email

        # Send email to both plaintiff and defendant
        send_mail(
            'Case Deletion Notification',
            f'Your case has been deleted for the following reason: {reason}',
            from_email=settings.DEFAULT_FROM_EMAIL,  # Ensure this is set in settings
            recipient_list=[plaintiff_email, defendant_email],  # List of recipients
            fail_silently=False,  # Raise errors if email sending fails
        )

        messages.success(request, 'Case deleted successfully.')
        return redirect('case_management')

    cases = Case.objects.all()
    return render(request, 'cases_management.html', {'cases': cases})

@login_required(login_url='/login/')
def case_status(request):
    cases = Case.objects.all()
    return render(request, 'case_status.html', {'cases': cases})

@login_required(login_url='/login/')
def all_cases(request):
    cases = Case.objects.all()
    return render(request, 'all_cases.html', {'cases': cases})

# Example view for Pending Cases
@login_required(login_url='/login/')
def pending_cases(request):
    cases = Case.objects.filter(status='PENDING')
    return render(request, 'pending_cases.html', {'cases': cases})

# Example view for Active Cases
@login_required(login_url='/login/')
def active_cases(request):
    cases = Case.objects.filter(status='ACTIVE')
    return render(request, 'active_cases.html', {'cases': cases})

# Example view for Closed Cases
@login_required(login_url='/login/')
def closed_cases(request):
    cases = Case.objects.filter(status='CLOSED')
    return render(request, 'closed_cases.html', {'cases': cases})

# Example view for Dismissed Cases
@login_required(login_url='/login/')
def dismissed_cases(request):
    cases = Case.objects.filter(status='DISMISSED')
    return render(request, 'dismissed_cases.html', {'cases': cases})

@login_required(login_url='/login/')
def add_judge(request):
    if request.method == 'POST':
        username = request.POST['username']
        full_name = request.POST['full_name']
        email = request.POST['email']
        contact_number = request.POST['contact_number']
        password = request.POST['password']
        address = request.POST['address']
        court = request.POST['court']

        # Validation
        errors = []

        # General validations
        if not all([username, full_name, email, password, address, court]):
            errors.append("All fields are required.")

        if User.objects.filter(username=username).exists():
            errors.append("Username already exists.")
         # Validate email format
        try:
            validate_email(email)  # Django's built-in email validator
        except ValidationError:
            errors.append("Invalid email format.")
        else:
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                errors.append("Email is already registered.")

        # Validate contact number format
        if not re.fullmatch(r'^\d{10}$', contact_number):
            errors.append("Contact number must be exactly 10 digits.")
       
        # password validation
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if not re.search(r'[A-Z]', password):
            errors.append("Must contain an uppercase letter.")
        if not re.search(r'[a-z]', password):
            errors.append("Must contain a lowercase letter.")
        if not re.search(r'\d', password):
            errors.append("Must contain a digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Must contain a special character.")
        if re.search(r'\s', password):
            errors.append("Must not contain spaces.")
        # Check if contact number already exists
        if User.objects.filter(contact_number=contact_number).exists():
            errors.append("Contact number is already registered.")

        # If there are any errors, display them all and redirect to signup
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('add_judge')

        user = User.objects.create_user(username=username, password=password, email=email, full_name=full_name, contact_number=contact_number, address=address, user_type='JUDGE')
        Judge.objects.create(user=user, court=court)
        messages.success(request, 'Judge added successfully.')
        send_mail(
            'Judge Registration',
            f'You have been registered as a judge with the following details:\n\n'
            f'Username: {username}\n Password: {password} \n Full Name: {full_name}\n Email: {email} \n Contact Number: {contact_number}\n Address: {address}\n Allocated Court: {court}\n'
            f'Please log in to your account to start using the system.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return redirect('add_judge')
    return render(request, 'add_judge.html')

@login_required(login_url='/login/')
def lawyer_approve_reject(request):
    lawyers = Lawyer.objects.filter(user__is_active=False)
    return render(request, 'lawyer_requests.html', {'lawyers': lawyers})

@login_required(login_url='/login/')
def lawyer_approve(request):
    user = get_object_or_404(User, username=request.GET['username'])
    try:
        lawyer = Lawyer.objects.get(user=user)
    except Lawyer.DoesNotExist:
        messages.error(request, "This user is not a lawyer.")
        return redirect('admin_dashboard')
    lawyer.user.user_type = 'LAWYER'
    lawyer.user.is_active = True
    lawyer.user.save()
    messages.success(request, f"Lawyer {user.username} has been approved.")
    # Notify lawyer of approval
    lawyer.user.email_user(
        'Approval Notification',
        'Congratulations, your lawyer account has been approved. now you can login into your account.',
        'ecourtofficially@gmail.com'
    )

    return redirect('lawyer_approve_reject')


@login_required(login_url='/login/')
def lawyer_reject(request):
    user = get_object_or_404(User, username=request.GET['username'])
    try:
        lawyer = Lawyer.objects.get(user=user)
    except Lawyer.DoesNotExist:
        messages.error(request, "This user is not a lawyer.")
        return redirect('admin_dashboard')

        
    lawyer.delete()
    messages.success(
        request, f"Lawyer {user.username} has been rejected.")
    # Notify lawyer of rejection
    user.email_user(
        'Rejection Notification',
        'We regret to inform you that your lawyer account has been rejected.',
        'ecourtofficially@gmail.com'
    )

    return redirect('lawyer_approve_reject')

@login_required(login_url='/login/')
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})

@login_required(login_url='/login/')
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        # This line is unnecessary, you can remove it as username is readonly and not changing
        user.username = user.username

        user.email = request.POST.get('email', user.email)
        user.contact_number = request.POST.get(
            'contact_number', user.contact_number)

        profile_image = request.FILES.get('profile_picture')
        if profile_image:
            user.profile_picture = profile_image

        # Add validations
        if not user.email:
            messages.error(request, 'Email is required')
            return redirect('edit_profile')
        else:
            try:
                validate_email(user.email)  # Validate email format
            except ValidationError:
                messages.error(request, 'Invalid email address')
                return redirect('edit_profile')

        if not user.contact_number:
            messages.error(request, 'Contact number is required')
            return redirect('edit_profile')
        elif not user.contact_number.isdigit() or len(user.contact_number) != 10:  # Adjust length as per requirement
            messages.error(
                request, 'Invalid phone number. It should be 10 digits long.')
            return redirect('edit_profile')

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('edit_profile')

    return render(request, 'edit_profile.html', {'user': user})

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

@login_required(login_url='/login/')
def analytics_dashboard(request):
    # Fetch data for cases
    cases = Case.objects.all()
    case_status_counts = cases.values('status').annotate(count=Count('status'))
    cases_data = {
        'labels': [status['status'] for status in case_status_counts],
        'data': [status['count'] for status in case_status_counts],
        'label': 'Cases'
    }

    # Fetch data for lawyers
    lawyers = Lawyer.objects.all()
    lawyer_case_counts = cases.values('assigned_lawyer__user__full_name').annotate(count=Count('id'))
    lawyers_data = {
        'labels': [lawyer['assigned_lawyer__user__full_name'] for lawyer in lawyer_case_counts],
        'data': [lawyer['count'] for lawyer in lawyer_case_counts],
        'label': 'Cases per Lawyer'
    }

    # Fetch data for judges
    judges = Judge.objects.all()
    judge_case_counts = cases.values('assigned_judge__user__full_name').annotate(count=Count('id'))
    judges_data = {
        'labels': [judge['assigned_judge__user__full_name'] for judge in judge_case_counts],
        'data': [judge['count'] for judge in judge_case_counts],
        'label': 'Cases per Judge'
    }

    # Fetch data for citizens
    citizens = Citizen.objects.all()
    citizens_data = {
        'labels': ['Total Citizens'],
        'data': [citizens.count()],
        'label': 'Citizens'
    }

    # Fetch data for case types
    case_types = cases.values('case_type').annotate(count=Count('case_type'))
    case_types_data = {
        'labels': [case_type['case_type'] for case_type in case_types],
        'data': [case_type['count'] for case_type in case_types],
        'label': 'Case Types'
    }

    # Fetch data for monthly cases
    monthly_cases = cases.annotate(month=TruncMonth('case_filed_date')).values('month').annotate(count=Count('id')).order_by('month')
    monthly_cases_data = {
        'labels': [month['month'].strftime('%B %Y') for month in monthly_cases],
        'data': [month['count'] for month in monthly_cases],
        'label': 'Monthly Cases'
    }

    # Fetch data for hearings
    hearings = Hearing.objects.all()
    hearing_counts = hearings.values('date').annotate(count=Count('id'))
    hearings_data = {
        'labels': [hearing['date'].strftime('%Y-%m-%d') for hearing in hearing_counts],
        'data': [hearing['count'] for hearing in hearing_counts],
        'label': 'Hearings'
    }

    # Fetch data for documents
    documents = Document.objects.all()
    document_counts = documents.values('document_type').annotate(count=Count('id'))
    documents_data = {
        'labels': [document['document_type'] for document in document_counts],
        'data': [document['count'] for document in document_counts],
        'label': 'Documents'
    }

    # Fetch data for payments
    payments = Payment.objects.all()
    payment_status_counts = payments.values('status').annotate(count=Count('status'))
    payments_data = {
        'labels': [status['status'] for status in payment_status_counts],
        'data': [status['count'] for status in payment_status_counts],
        'label': 'Payments'
    }

    context = {
        'cases_data': json.dumps(cases_data),
        'lawyers_data': json.dumps(lawyers_data),
        'judges_data': json.dumps(judges_data),
        'citizens_data': json.dumps(citizens_data),
        'case_types_data': json.dumps(case_types_data),
        'monthly_cases_data': json.dumps(monthly_cases_data),
        'hearings_data': json.dumps(hearings_data),
        'documents_data': json.dumps(documents_data),
        'payments_data': json.dumps(payments_data)
    }

    return render(request, 'analytics.html', context)

def reports_dashboard(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')

        # Prepare data and headers dynamically
        headers = []
        data = []
        report_title = ""

        if report_type == 'cases':
            cases = Case.objects.select_related(
                'plaintiff', 'defendant', 'assigned_judge')
            headers = ["Case Number", "Case Title", "Status",
                       "Case Type", "Plaintiff", "Defendant", "Assigned Judge"]
            report_title = "Cases Report"

            for case in cases:
                row = [
                    case.case_number,
                    case.case_title,
                    case.status,
                    case.case_type,
                    case.plaintiff.user.full_name if case.plaintiff else "N/A",
                    case.defendant.user.full_name if case.defendant else "N/A",
                    case.assigned_judge.user.full_name if case.assigned_judge else "N/A",
                ]
                data.append(row)

        elif report_type == 'lawyers':
            lawyers = Lawyer.objects.select_related('user')
            headers = ["Full Name", "License Number",
                       "Law Firm", "Contact Number"]
            report_title = "Lawyers Report"

            for lawyer in lawyers:
                row = [
                    lawyer.user.full_name,
                    lawyer.license_number,
                    lawyer.law_firm,
                    lawyer.user.contact_number,
                ]
                data.append(row)

        elif report_type == 'judges':
            judges = Judge.objects.select_related('user')
            headers = ["Full Name", "Court", "Cases Assigned"]
            report_title = "Judges Report"

            for judge in judges:
                row = [
                    judge.user.full_name,
                    judge.court,
                    judge.cases_assigned,
                ]
                data.append(row)

        elif report_type == 'citizens':
            citizens = Citizen.objects.select_related('user')
            headers = ["Full Name", "National ID",
                       "Cases Filed", "Contact Number"]
            report_title = "Citizens Report"

            for citizen in citizens:
                row = [
                    citizen.user.full_name,
                    citizen.national_id,
                    citizen.cases_filed,
                    citizen.user.contact_number,
                ]
                data.append(row)

        elif report_type == 'caseTypes':
            case_types = Case.objects.values(
                'case_type').annotate(case_count=Count('id'))
            headers = ["Case Type", "Case Count"]
            report_title = "Case Types Report"

            for case_type in case_types:
                row = [
                    case_type['case_type'],
                    case_type['case_count'],
                ]
                data.append(row)

        elif report_type == 'monthlyCases':
            monthly_cases = Case.objects.annotate(month=TruncMonth(
                'case_filed_date')).values('month').annotate(case_count=Count('id'))
            headers = ["Month", "Case Count"]
            report_title = "Monthly Cases Report"

            for monthly_case in monthly_cases:
                row = [
                    monthly_case['month'].strftime(
                        '%B %Y') if monthly_case['month'] else "N/A",
                    monthly_case['case_count'],
                ]
                data.append(row)

        elif report_type == 'hearings':
            hearings = Hearing.objects.select_related('case')
            headers = ["Case Number", "Hearing Date",
                       "Hearing Time", "Outcome"]
            report_title = "Hearings Report"

            for hearing in hearings:
                row = [
                    hearing.case.case_number if hearing.case else "N/A",
                    hearing.date.strftime(
                        '%Y-%m-%d') if hearing.date else "N/A",
                    hearing.time.strftime('%H:%M') if hearing.time else "N/A",
                    hearing.outcome,
                ]
                data.append(row)

        elif report_type == 'documents':
            documents = Document.objects.select_related('case', 'uploaded_by')
            headers = ["Case Number", "Document Type",
                       "Uploaded By", "Uploaded At"]
            report_title = "Documents Report"

            for document in documents:
                row = [
                    document.case.case_number if document.case else "N/A",
                    document.document_type,
                    document.uploaded_by.user.full_name if document.uploaded_by else "N/A",
                    document.uploaded_at.strftime(
                        '%Y-%m-%d %H:%M') if document.uploaded_at else "N/A",
                ]
                data.append(row)

        elif report_type == 'payments':
            payments = Payment.objects.select_related('case')
            headers = ["Order ID", "Case Number", "Amount", "Status", "Requested At", "Paid At"]
            report_title = "Payments Report"

            for payment in payments:
                row = [
                    payment.order_id,
                    payment.case.case_number if payment.case else "N/A",
                    payment.amount,
                    payment.status,
                    payment.requested_at.strftime('%Y-%m-%d %H:%M') if payment.requested_at else "N/A",
                    payment.paid_at.strftime('%Y-%m-%d %H:%M') if payment.paid_at else "N/A",
                ]
                data.append(row)

        else:
            return HttpResponse("Invalid report type", status=400)

        # Prepare the PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={report_type}_report.pdf'

        # Create a SimpleDocTemplate
        pdf = SimpleDocTemplate(response, pagesize=letter)

        # Add a title to the report
        styles = getSampleStyleSheet()
        title = Paragraph(f"<strong>{report_title}</strong>", styles['Title'])
        spacer = Spacer(1, 20)  # Add some space after the title

        # Prepare data for the table
        table_data = [headers] + data  # Add headers as the first row

        # Create the table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0),
             colors.HexColor("#1e3c72")),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all text
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Padding for header
            # Alternate row background
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines
        ]))

        # Build the PDF with title, spacer, and table
        elements = [title, spacer, table]
        pdf.build(elements)

        return response

    return render(request, 'reports.html')

@login_required(login_url='/login/')
def contact_us_reply(request):
    # Clear all previous messages
    storage = messages.get_messages(request)
    storage.used = True

    if request.method == 'POST':
        contact_id = request.POST.get('contact_id')
        reply_message = request.POST.get('reply_message')
        contact = get_object_or_404(ContactUs, id=contact_id)
        contact.delete()
        
        # Send email to the user with the reply message
        send_mail(
            f'Reply to Your Query: {contact.subject}',
            reply_message,
            settings.DEFAULT_FROM_EMAIL,
            [contact.email],
            fail_silently=False,
        )
        
        messages.success(request, 'Reply sent successfully.')
        return redirect('contact_us_reply')

    contacts = ContactUs.objects.all()
    return render(request, 'contactus_reply.html', {'contacts': contacts})

@login_required(login_url='/login/')
def view_payments(request):
    Completed = Payment.objects.filter(status='Completed')
    Failed = Payment.objects.filter(status='Failed')
    payments = Completed | Failed
    return render(request, 'view_payments.html', {'payments': payments})

@login_required(login_url='/login/')
def proceed_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.proceed = True
    payment.save()

    # Send confirmation email to the lawyer
    lawyer = Lawyer.objects.get(user__email=payment.lawyer_email)
    send_mail(
        'Payment Proceeded',
        f'Dear {lawyer.user.full_name},\n\nYour payment for case {payment.case.case_number} has been proceeded successfully.\n\nBest regards,\neCourt Team',
        'ecourtofficially@gmail.com',
        [payment.lawyer_email],
        fail_silently=False,
    )

    messages.success(request, 'Payment proceeded successfully.')
    return redirect('view_payments')