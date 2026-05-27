from datetime import datetime, timedelta, timezone
from common.helpers.model_helpers.preference import (
    get_unique_langaues_list,
    make_language_queryset_list_unique,
)
from common.utils.auth import admin_required
from django.db.models import Q

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import HttpResponseRedirect
from preference.models import Language
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.staticfiles import finders

from users.tasks import send_email_notification
from users.utils import get_user_destinations, get_user_factories, get_user_organisations
from common.utils.posthog_helper import track_event, identify_user
from preference.models import DashboardPreferences, ChartSettings
from preference.dashboard_config import get_default_dashboard_preferences, CHART_DEFINITIONS
from preference.views import get_available_charts
from .forms import (
    ChangeEmailForm,
    CreateUserForm,
    EditUserForm,
    InviteUserForm,
    LoginForm,
    RequestPasswordResetForm,
    SetPasswordForm,
    UpdateUserProfileForm,
    UserMgtForm,
    CreateNewUserForm,
)
from .models import User, UserInvitations, UserSession
from users.templatetags.user_role_tags import has_group

from django.utils.translation import gettext as _ 


def initialize_user_dashboard_preferences(user, request=None):
    """Initialize dashboard preferences for a newly created user"""
    try:
        if request is None:
            class MockRequest:
                def __init__(self, user):
                    self.user = user
            mock_request = MockRequest(user)
        else:
            mock_request = request
        
        available_charts = get_available_charts(user, mock_request)

        if not available_charts:
            available_charts = list(CHART_DEFINITIONS.keys())

        default_prefs = get_default_dashboard_preferences(available_charts)

        dashboard_prefs = DashboardPreferences.objects.create(
            user=user,
            layout=default_prefs['layout'],
            chart_definitions=default_prefs['chart_definitions'],
            filter_start_date=None,
            filter_end_date=None
        )

        for chart_id in available_charts:
            if chart_id in CHART_DEFINITIONS:
                ChartSettings.objects.create(
                    dashboard_preferences=dashboard_prefs,
                    chart_id=chart_id,
                    chart_type=CHART_DEFINITIONS[chart_id]['default_type'],
                    size=CHART_DEFINITIONS[chart_id]['default_size'],
                    enabled=True,
                    start_date=None,
                    end_date=None
                )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error initializing dashboard preferences for user {user.email}: {str(e)}')

@login_required
@admin_required
def list_users(request):
    search_query = request.GET.get('search', '')
    group_id = request.GET.get('group', '')
    page_number = request.GET.get('page', 1)
    items_per_page = request.GET.get('items_per_page', 25)

    users = User.objects.filter(is_deleted=False)

    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query)
        )

    if group_id:
        users = users.filter(groups__id=group_id)

    users = users.order_by("-id")
    groups = Group.objects.all()

    paginator = Paginator(users, int(items_per_page))
    page_obj = paginator.get_page(page_number)

    context = {
        'users': page_obj,
        'groups': groups,
        'paginator': paginator,
        'search_query': search_query,
        'group_id': group_id,
        'items_per_page': items_per_page
    }

    return render(request, "users/list_users.html", context)


@login_required
@admin_required
def list_invitations(request):
    invitations = UserInvitations.objects.all()
    return render(request, template_name="users/list_invitations.html", context={"invitations": invitations})


@login_required
def logout_user(request):
    if 'login_time' in request.session:
        login_time = datetime.fromisoformat(request.session['login_time'])
        logout_time = datetime.now(timezone.utc)
        session_duration = (logout_time - login_time).total_seconds()
        
        try:
            latest_session = UserSession.objects.filter(
                user_id=request.session['user_id'],
                logout_time__isnull=True
            ).latest('login_time')
            latest_session.logout_time = logout_time
            latest_session.save()
        except UserSession.DoesNotExist:
            pass
        
        request.session['logout_time'] = logout_time.isoformat()
        request.session['session_duration'] = session_duration
        
        user_id = request.session.get('user_id')
        if user_id:
            track_event(
                event_name="user_logged_out",
                user_id=str(user_id),
                properties={
                    "session_duration_seconds": session_duration,
                    "session_duration_hours": round(session_duration / 3600, 2),
                },
                request=request
            )
        
        request.session.flush()
        
        logout(request)
        return redirect("users:login_user")
    
    logout(request)
    return redirect("users:login_user")


def create_user_account(request):
    logout(request)
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            
            initialize_user_dashboard_preferences(user, request)
            
            track_event(
                event_name="user_signed_up",
                user_id=str(user.id),
                user_email=user.email,
                properties={
                    "signup_method": "email",
                    "is_active": user.is_active,
                },
                request=request
            )
            identify_user(
                user_id=str(user.id),
                user_email=user.email,
                properties={
                    "first_name": getattr(user, 'first_name', ''),
                    "last_name": getattr(user, 'last_name', ''),
                },
                request=request
            )
            messages.info(request, _("createUserAccountViewInfo"))
            return redirect("users:login_user")
        else:
            track_event(
                event_name="user_signup_failed",
                properties={
                    "errors": form.errors,
                },
                request=request
            )
            messages.error(request, _("createUserAccountViewError"))
    return render(request, "users/sign_up.html", context={"form": form})


def login_user(request):
    logout(request)
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            try:
                user = User.objects.get(email__iexact=email)
                user = authenticate(request, username=user.email, password=password)
                if user is not None:
                    if has_group(user, "worker"):
                        track_event(
                            event_name="user_login_failed",
                            user_id=str(user.id),
                            user_email=user.email,
                            properties={
                                "reason": "worker_dashboard_access_denied",
                            },
                            request=request
                        )
                        messages.error(
                            request,
                            "This account is not allowed to access the dashboard.",
                        )
                        return render(request, "users/sign_in.html", {"form": form})
                    login(request, user)
                    UserSession.objects.create(user=user)
                    request.session['login_time'] = datetime.now(timezone.utc).isoformat()
                    request.session['user_email'] = user.email
                    request.session['user_id'] = user.id
                    request.session['user_role'] = user.groups.first().name if user.groups.exists() else 'No Role'

                    track_event(
                        event_name="user_logged_in",
                        user_id=str(user.id),
                        user_email=user.email,
                        properties={
                            "user_role": request.session.get('user_role'),
                            "is_staff": user.is_staff,
                        },
                        request=request
                    )
                    identify_user(
                        user_id=str(user.id),
                        user_email=user.email,
                        request=request
                    )

                    if has_group(user, "Summerberry"):
                        return redirect("dashboard:summerberry-dashboard")
                    else:
                        return redirect("preference:user_overview")
                else:
                    track_event(
                        event_name="user_login_failed",
                        user_email=email,
                        properties={
                            "reason": "invalid_password",
                        },
                        request=request
                    )
                    messages.error(request, _("loginUserViewError"))
            except User.DoesNotExist:
                messages.error(request, _("loginUserViewErrorNotUser"))
        else:
            messages.error(request, _("loginUserViewInvalidForm"))
    return render(request, "users/sign_in.html", {"form": form})


@login_required
def manage_account(request, id):
    user = User.objects.get(id=id)
    form = UserMgtForm(instance=user)
    if request.method == "POST":
        form = UserMgtForm(data=request.POST, instance=user)
        if form.is_valid:
            form.save()
    return render(request, "users/manage_user.html", context={"form": form, "user": user})


@login_required
@admin_required
def activate_account(request, id):
    return_page = request.GET.get('return_page', '1')
    search_query = request.GET.get('search', '')
    group_id = request.GET.get('group', '')
    items_per_page = request.GET.get('items_per_page', '25')
    
    user = User.objects.get(id=id)
    subject = "Your account at JGW Data Dashboard."
    deactivation_message = (
        f"Hello\n, Your account at Just Good Work Data Platform has been deactivated.\n"
        f"\nPlease reach out to the administrator if this action was not initiated by you."
        f"\n\nJust Good Work Data Platform"
    )
    activation_message = (
        f"Hello\n, Your account at JGW Pandas has been activated.\n"
        f"\n Please reach out to the administrator if this account was not created by you."
        f"\nJust Good Work Data Platform"
    )
    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f"The user account: {user.email} was deactivated successfully.")
        send_email_notification.delay(
            subject=subject,
            message=deactivation_message,
            recipients=[user.email],
            attachment_path=None,
            html_message=None,
            inline_images=None
        )
    elif user.is_active == False:
        user.is_active = True
        user.save()
        messages.success(request, f"The user account: {user.email} was activated successfully.")
        send_email_notification.delay(
            subject=subject,
            message=activation_message,
            recipients=[user.email],
            attachment_path=None,
            html_message=None,
            inline_images=None
        )
    
    return_params = {
        'page': return_page,
        'search': search_query,
        'group': group_id,
        'items_per_page': items_per_page
    }
    base_url = reverse('users:list_users')
    query_string = '&'.join(f"{key}={value}" for key, value in return_params.items() if value)
    return_url = f"{base_url}?{query_string}" if query_string else base_url
    
    return redirect(return_url)


def generate_token(payload_data=None, days_to_expiry=1):
    """Returns a jwt token that expires in `days_to_expiry` days

    Args:
        payload_data: any extra data apart from the exp claimset to encode in the token.
        days_to_expiry: number of days after creation token expires.

    Returns:
        token: jwt token string encoded with settings.SECRET_KEY
    """
    payload = {"exp": datetime.now(tz=timezone.utc) + timedelta(days=days_to_expiry)}
    if payload_data:
        payload.update(payload_data)
    token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")
    return token


@login_required
@admin_required
def invite_user(request):
    form = InviteUserForm()
    if request.method == "POST":
        form = InviteUserForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data.get("email")
            invite = form.save(commit=True)
            token = generate_token(payload_data={"invite_id": invite.id}, days_to_expiry=3)
            send_email_notification.delay(
                subject="Set up your account on Just Good Work Data Platform",
                message=f"""
                Please follow this link to set up your new account on Just Good Work Data Platform:
                https://data.justgood.work{reverse("users:verify_invite", args=(token,))}
                \nPlease note that this link expires in 3 days.
                """,
                recipients=[email_address],
                attachment_path=None,
                html_message=None,
                inline_images=None
            )
            messages.info(request, "The invitation email will be sent out shortly.")
            return redirect("users:list_users")
        else:
            messages.error(request, "Error validating form!")
    return render(request, "users/invite_user.html", context={"form": form})


def verify_invite(request, token):
    logout(request)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        invite = UserInvitations.objects.get(id=payload.get("invite_id"))
        invite.status = "ACCEPTED"
        invite.save()
        token = generate_token(payload_data={"invite_id": invite.id}, days_to_expiry=1)
        return redirect(reverse("users:set_password", args=(token,)))
    except jwt.ExpiredSignatureError:
        messages.error(request, "This link is expired!")
    except UserInvitations.DoesNotExist:
        messages.error(request, "Invitation not found!")
    return render(request, "users/handle_invite.html")


@login_required
def profile(request):
    profile = User.objects.get(id=request.user.id)

    if request.method == "POST":
        form = UpdateUserProfileForm(request.POST or None, instance=request.user)
        if not request.GET.get("tab") or request.GET.get("tab") == "profile":
            if form.is_valid():
                profile.first_name = form.cleaned_data.get("first_name")
                profile.last_name = form.cleaned_data.get("last_name")
                profile.email = form.cleaned_data.get("email")
                profile.receive_marketing_emails = form.cleaned_data.get("receive_marketing_emails")
                profile.save()
                messages.info(request, "Profile updated successfully!")
            else:
                messages.error(request, "Error validating form!")

        if request.GET.get("tab") == "password":
            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password == confirm_password:
                if request.user.check_password(old_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, "Password successfully changed!")
                    logout(request)
                    return redirect("users:login_user")
                else:
                    messages.error(request, "Old password does not match!")
            else:
                messages.error(request, "New password and confirm password do not match!")

    current_user = request.user

    user_factories = get_user_factories(current_user)
    user_organisations = get_user_organisations(current_user)
    user_destinations = get_user_destinations(current_user)

    user_languages = (
        get_unique_langaues_list()
        if current_user.is_superuser
        else make_language_queryset_list_unique(current_user.user_languages.all())
    )

    form = UpdateUserProfileForm(
        initial={
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "email": profile.email,
            "receive_marketing_emails": profile.receive_marketing_emails,
        }
    )
    context = {
        "profile": profile,
        "form": form,
        "user_factories": user_factories,
        "user_organisations": user_organisations,
        "user_destinations": user_destinations,
        "user_languages": user_languages,
    }
    return render(request, template_name="users/profile.html", context=context)


def request_password_reset(request):
    logout(request)
    form = RequestPasswordResetForm()

    if request.method == "POST":
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            email_address = form.cleaned_data.get("email")
            try:
                user = User.objects.filter(email__iexact=email_address).first()
                if not user:
                    raise User.DoesNotExist()
                token = generate_token(payload_data={"user_id": user.id}, days_to_expiry=1)
                reset_link = f"https://data.justgood.work{reverse('users:set_password', args=(token,))}"

                logo_path = finders.find("../static/logo.jpg")

                html_content = render_to_string(
                    "users/password_reset_email.html",
                    {"reset_link": reset_link, "logo_cid": "logo_cid"}
                )
                plain_message = strip_tags(html_content)

                send_email_notification(
                    subject=_("requestPasswordResetViewEmailSubject"),
                    message=plain_message,
                    recipients=[email_address],
                    attachment_path=None,
                    html_message=html_content,
                    inline_images={"logo_cid": logo_path} if logo_path else None
                )

                success_text = _("requestPasswordResetViewEmailSuccessText").format(email_address=email_address)

                return render(request, "users/email_sent.html", {"success_text": success_text})

            except User.DoesNotExist:
                form.full_clean()
                messages.error(request, _("requestPasswordResetViewErrorMessage"))

    return render(request, "users/request_password_reset.html", {"form": form})

def set_password(request, token):
    logout(request)
    form = SetPasswordForm()
    invite = None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id, invite_id = payload.get("user_id"), payload.get("invite_id")

        if invite_id is None and user_id is None:
            messages.error(request, _("setPasswordViewInvalidTokenError"))
            return render(request, "users/set_password.html", {"form": form})
        if invite_id is not None:
            invite = UserInvitations.objects.filter(id=invite_id).first()
            if not invite:
                messages.error(request, _("setPasswordViewInvalidTokenError"))
                return render(request, "users/set_password.html", {"form": form})
            if invite.status == "ACCEPTED":
                messages.error(request, _("setPasswordViewInvalidTokenError"))
                return render(request, "users/set_password.html", {"form": form})
            if user_id and not User.objects.filter(id=user_id, email__iexact=invite.email).exists():
                messages.error(request, _("setPasswordViewInvalidTokenError"))
                return render(request, "users/set_password.html", {"form": form})

        if request.method == "POST":
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get("confirm_password")
                access_type = 'dashboard'
                if user_id:
                    user = User.objects.get(id=user_id)
                    user.set_password(password)
                    user.save()
                    access_type = user.access_type
                else:
                    user_obj = {"email": invite.email, "role": invite.scheme_id}
                    new_user = User.objects.create_user(**user_obj, password=password, is_active=True)
                    if invite.phone_number:
                        new_user.phone_number = invite.phone_number
                        new_user.save(update_fields=["phone_number"])
                    access_type = new_user.access_type
                    if invite.organisation:
                        new_user.organisation_data.add(invite.organisation)
                    # Initialize dashboard preferences for the new user
                    initialize_user_dashboard_preferences(new_user, request)
                    if invite:
                        invite.status = "ACCEPTED"
                        invite.save(update_fields=["status"])
                success_text = _("setPasswordViewSuccessText")
                
                return render(
                    request,
                    "users/email_sent.html",
                    {
                        "success_text": success_text,
                        "access_type": access_type,
                    },
                )
            else:
                messages.error(request, _("setPasswordViewInvalidFormError"))
    except jwt.ExpiredSignatureError:
        messages.error(request, _("setPasswordViewLinkExpiredError"))
    except User.DoesNotExist:
        messages.error(request, _("setPasswordViewUserAccountNotFound"))
    return render(request, "users/set_password.html", {"form": form})


@login_required
def change_email_address(request):
    user = request.user
    old_email = user.email
    form = ChangeEmailForm()
    if request.method == "POST":
        logout(request)
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data.get("new_email")
            if new_email == old_email:
                messages.error(request, "New email must be different from current email!")
            elif User.objects.filter(email=new_email):
                messages.error(request, "A user with this email address already exists!")
            else:
                token = generate_token(
                    payload_data={"user_id": user.id, "new_email": new_email}, days_to_expiry=1
                )
                send_email_notification.delay(
                    subject="Verify your email",
                    message=f"""
                    \n Click this link to verify this email for your account on Just Good Work Data Platform:
                    \n https://data.justgood.work{reverse("users:verify_email", args=(token,))}
                    \n This link expires in 1 day.
                    \n Reach out to your administrator if you didn't initiate this action.
                    """,
                    recipients=[new_email],
                    attachment_path=None,
                    html_message=None,
                    inline_images=None
                )
                success_text = f"""
                    An email has been sent to {new_email}.
                    Please check for an email from Just Good Work Data Platform and click on the included link to verify the change in email address.
                    """
                return render(
                    request, template_name="users/email_sent.html", context={"success_text": success_text}
                )
        else:
            messages.error(request, "Error validating form!")
    return render(request, template_name="users/change_email.html", context={"form": form})


def verify_email_change(request, token):
    logout(request)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id, new_email = payload.get("user_id"), payload.get("new_email")
        if user_id and new_email:
            user = User.objects.get(id=user_id)
            user.email = new_email
            user.save()
        else:
            messages.error(request, "Invalid token!")
    except jwt.ExpiredSignatureError:
        messages.error(request, "This link is expired!")
    except User.DoesNotExist:
        messages.error(request, "User account not found!")
    return redirect("users:login_user")


@login_required
@admin_required
def create_or_edit_user(request, user_id=None):
    if user_id:
        return update_user(request, user_id)
    else:
        return create_user(request)


def create_user(request):
    form = CreateNewUserForm()
    if request.method == "POST":
        form = CreateNewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = True

            user_languages = form.cleaned_data.get("user_languages", [])
            langs_from_ids = Language.objects.filter(id__in=user_languages).values_list(
                "translated_name", flat=True
            )
            all_langs = Language.objects.filter(translated_name__in=langs_from_ids)

            user.save()
            form.save_m2m()  # Save the many-to-many relationships

            new_user = User.objects.filter(id=user.id).first()
            new_user.user_languages.clear()
            for lang in all_langs:
                new_user.user_languages.add(lang)

            # Initialize dashboard preferences for the new user
            initialize_user_dashboard_preferences(new_user, request)

            messages.success(request, f"User {user.email} created successfully!")
            return render(request, "users/create_user.html", context={"form": CreateNewUserForm(), "show_modal": True})

    return render(request, "users/create_user.html", context={"form": form, "show_modal": False})


def update_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    # Get return parameters
    return_page = request.GET.get('return_page', '1')
    search_query = request.GET.get('search', '')
    group_id = request.GET.get('group', '')
    items_per_page = request.GET.get('items_per_page', '25')
    
    form = EditUserForm(request.POST or None, instance=user)
    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)

            user_languages = form.cleaned_data.get("user_languages", [])
            langs_from_ids = Language.objects.filter(id__in=user_languages).values_list(
                "translated_name", flat=True
            )
            all_langs = Language.objects.filter(translated_name__in=langs_from_ids)

            user.save()
            form.save_m2m()

            edited_user = User.objects.filter(id=user.id).first()
            edited_user.user_languages.clear()
            for lang in all_langs:
                edited_user.user_languages.add(lang)

            messages.success(request, "User updated successfully!")
            
            # Construct return URL with all parameters
            return_params = {
                'page': return_page,
                'search': search_query,
                'group': group_id,
                'items_per_page': items_per_page
            }
            base_url = reverse('users:list_users')
            query_string = '&'.join(f"{key}={value}" for key, value in return_params.items() if value)
            return_url = f"{base_url}?{query_string}" if query_string else base_url
            
            return redirect(return_url)

    context = {
        'form': form,
        'return_page': return_page,
        'search_query': search_query,
        'group_id': group_id,
        'items_per_page': items_per_page
    }
    return render(request, "users/edit_user.html", context=context)
