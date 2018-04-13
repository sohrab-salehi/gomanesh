from django.contrib import admin
from .models import *


admin.site.register(Contest)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Group)
admin.site.register(GroupTeam)
admin.site.register(Match)
admin.site.register(MatchTeam)

