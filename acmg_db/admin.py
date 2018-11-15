from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Variant)
admin.site.register(Gene)
admin.site.register(Transcript)
admin.site.register(TranscriptVariant)
admin.site.register(Classification)
