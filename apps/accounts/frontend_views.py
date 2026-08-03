from django.contrib.auth.views import LoginView


class CoffeeTraceLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
