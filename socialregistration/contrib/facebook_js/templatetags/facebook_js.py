from django import template

from socialregistration.templatetags import button

register = template.Library()

register.tag('facebook_js_button', button('socialregistration/facebook_js/facebook_button.html'))