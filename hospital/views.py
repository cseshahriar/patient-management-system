import logging
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from patient_ms.models import Patient
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, DetailView, TemplateView, View

from hospital.models import Contact, Feedback, Faq
from .models import Slider, Service, Doctor, Faq, Gallery
from hospital.forms import CustomLoginForm
from hospital.uility import user_has_group
from patient_ms.models import DoctorAppointment
from patient_ms.variable import (
    doctor_group,
    patient_group
)
logger = logging.getLogger(__name__)


class DoctorDashboard(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorDashboard, self).get_context_data(**kwargs)
        today = datetime.date.today()

        try:
            total_appointment = DoctorAppointment.objects.filter(
                doctor__user=self.request.user
            ).count()
            todays_appointment = DoctorAppointment.objects.filter(
                doctor__user=self.request.user,
                appointment_day=today
            ).count()
        except Exception as e:
            logging.warning(self.request, f'Unable to get data {e}')
            todays_appointment = 0
            total_appointment = 0

        doctor = get_object_or_404(Doctor, user=self.request.user)
        kwargs["doctor"] = doctor
        kwargs["doctor_count"] = Doctor.objects.all().count()
        kwargs["patient_count"] = Patient.objects.all().count()
        kwargs["total_appointment"] = total_appointment
        kwargs["todays_appointment"] = todays_appointment
        return kwargs


class HomeView(ListView):
    template_name = 'hospital/index.html'
    queryset = Service.objects.filter(is_active=True, is_deleted=False)
    context_object_name = 'services'
    form_class = CustomLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['sliders'] = Slider.objects.filter(
            is_active=True, is_deleted=False)
        context['experts'] = Doctor.objects.filter(
            is_active=True, is_deleted=False)
        context['form'] = self.form_class
        try:
            doctor = Doctor.objects.filter(user=self.request.user).first()
            if doctor:
                context['login_user'] = doctor
        except Exception as e:
            logger.debug(self.request, f"Doctor profile Not available {e}")

        try:
            patient = Patient.objects.filter(user=self.request.user).first()
            if patient:
                context['login_user'] = patient
                context['patient'] = patient
        except Exception as e:
            logger.debug(self.request, f"patient profile Not available {e}")

        context['feedback_list'] = Feedback.objects.filter(
            is_active=True).order_by('order')
        context['faq_list'] = Faq.objects.filter(
            is_active=True).order_by('order')
        return context


class LoginView(View):
    template_name = 'hospital/login.html'
    queryset = Service.objects.filter(is_active=True, is_deleted=False)
    form_class = CustomLoginForm

    def get(self, request):
        context = {"form": self.form_class}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(self.request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            user = authenticate(phone=phone, password=password)

            if user is not None and user.is_active:
                login(request, user)
                if user_has_group(user, doctor_group):
                    return redirect(self.get_doctor_url())
                if user_has_group(user, patient_group):
                    return redirect(self.get_patient_url())
                return redirect(self.get_success_url())
            else:
                messages.warning(
                    self.request,
                    "Invalid Phone Or Password"
                )
                context = {"form": self.form_class}
                return render(request, self.template_name, context)
        else:
            messages.warning(self.request, "Invalid Data")
            context = {"form": self.form_class}
            return render(request, self.template_name, context)

    def get_success_url(self):
        messages.success(self.request, "Login successfully!")
        logger.debug("Login successfully")
        return reverse_lazy("index")

    def get_doctor_url(self):
        messages.success(
            self.request, "Congratulations Doctor! You are Successfully Login"
        )
        logger.debug("Login successfully")
        return reverse_lazy("doctor_dashboard")

    def get_patient_url(self):
        messages.success(
            self.request, "Congratulations ! You are Successfully Login"
        )
        logger.debug("Login successfully")
        return reverse_lazy("patient_ms:patient_profile")




def logout_request(request):
    logout(request)
    messages.success(request, "Successfully Logout")
    return redirect("/")


class ServiceListView(ListView):
    queryset = Service.objects.filter(is_active=True, is_deleted=False)
    template_name = "hospital/services.html"


class ServiceDetailView(DetailView):
    queryset = Service.objects.filter(is_active=True, is_deleted=False)
    template_name = "hospital/service_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = Service.objects.all()
        return context


class DoctorListView(ListView):
    template_name = 'hospital/team.html'
    queryset = Doctor.objects.filter(is_active=True, is_deleted=False)
    paginate_by = 8


class DoctorDetailView(DetailView):
    template_name = 'hospital/team-details.html'
    model = Doctor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        related_doctor_list = Doctor.objects.filter(
            is_active=True, is_deleted=False
        ).exclude(pk=self.object.pk).distinct()
        context["related_doctor_list"] = related_doctor_list
        logger.info(f"{'*' * 10} related_doctor_list: {related_doctor_list}\n")
        return context


class FaqListView(ListView):
    template_name = 'hospital/faqs.html'
    queryset = Faq.objects.filter(is_active=True, is_deleted=False)


class GalleryListView(ListView):
    template_name = 'hospital/gallery.html'
    queryset = Gallery.objects.filter(is_active=True, is_deleted=False)
    paginate_by = 9


class ContactView(TemplateView):
    template_name = "hospital/contact.html"

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if subject == '':
            subject = "INFO"

        if name and message and email and phone:
            try:
                Contact.objects.create(
                    name=name, email=email,
                    phone=phone, subject=subject,
                    message=message
                )
                messages.success(request, "Submit")
            except Exception as e:
                logger.debug(request, f"Unable to take This request {e} ")
                messages.success(request, " Unable to take This request")

        return redirect('contact')
