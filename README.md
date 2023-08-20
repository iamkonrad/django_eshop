# django_eshop  (written in Django, using HTML and CSS)

## Some important points about this webapp:

1.DEFAULT ADMIN URL, default admin url IS NOT /admin, this project utilizes Honeypot; admin url path can be found inside the main app's (django_eshop) urls

2.USER AUTHORIZATION: For security reasons each person using this webapp needs to configure his/her own smtp settings, for now, only an EMAIL_BACKEND using django console handles that, but there are commented out lines in settings.py (the very bottom of the page) waiting to be filled with proper data in case there is a need to set profile update/password change/notifications/authorization handled by an smtp server (by default smtp server is set as Google);

3.IN ORDER TO TEST LOG-IN functionality without turning on smtp server: 1. register an account by clicking register account on the main page of the app and follow with the standard procedure, afterwards log-in to admin using superuser, set newly created test account status to ACTIVE(by default it's set to INACTIVE, since it needs to be activated by a link sent to an email address associated with your account), from now on you can log in with a newly created test account;

4.EXTERNAL PAYMENTS FUNCTIONALITY, similarly to smtp due to security reasons I haven't set this app to handle PayPal checkouts; once you proceed to the checkout and click on order checkout the order will be added to the database, where it can afterwards be accessed via admin panel;




## Some of the key functionalities:
