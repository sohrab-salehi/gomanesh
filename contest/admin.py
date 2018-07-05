from django.contrib import admin
from .models import *


admin.site.register(Profile)
admin.site.register(Contest)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(MatchTeam)
admin.site.register(Invitation)

