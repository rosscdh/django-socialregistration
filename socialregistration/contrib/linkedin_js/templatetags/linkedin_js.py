from django import template
from socialregistration.templatetags import button

register = template.Library()

register.tag('linkedin_js_button', button('socialregistration/linkedin_js/linkedin_button.html'))