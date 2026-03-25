from django import template
from django.template import TemplateSyntaxError

from user_management.permissions import is_flag_active

register = template.Library()


class FlagNode(template.Node):
    def __init__(self, flag_name, nodelist):
        self.flag_name = template.Variable(flag_name)
        self.nodelist = nodelist

    def render(self, context):
        request = context.get("request")
        selected_org_id = context.get("selected_org_id")
        try:
            flag_name = self.flag_name.resolve(context)
        except template.VariableDoesNotExist:
            return ""
        if is_flag_active(
            request,
            flag_name,
            selected_org_id=selected_org_id,
        ):
            return self.nodelist.render(context)
        return ""


@register.tag
def flag(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("flag tag requires a single flag name")
    flag_name = bits[1]
    nodelist = parser.parse(("endflag",))
    parser.delete_first_token()
    return FlagNode(flag_name, nodelist)
