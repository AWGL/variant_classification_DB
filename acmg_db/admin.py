from django.contrib import admin
from .models import *

class ClassificationAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'classification', 'classification_question', 'selected_first', 'strength_first', 'selected_second', 'strength_second',)
    search_fields = ('classification__id', 'classification_question__acmg_code', 'selected_first', 'strength_first', 'selected_second', 'strength_second',)
admin.site.register(ClassificationAnswer, ClassificationAnswerAdmin)

class ClassificationQuestionAdmin(admin.ModelAdmin):
    list_display = ('acmg_code', 'text', 'default_strength', 'allowed_strength_change',)
    search_fields = ('acmg_code', 'text', 'default_strength', 'allowed_strength_change',)
admin.site.register(ClassificationQuestion, ClassificationQuestionAdmin)

class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant', 'selected_transcript_variant', 'user_first_checker', 'user_second_checker', 'status',)
    search_fields = ('id',) # cant add variant as its split into chr,pos,ref,alt in model
    readonly_fields = ('variant', 'sample', 'selected_transcript_variant')
admin.site.register(Classification, ClassificationAdmin)

class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'comment',)
    search_fields = ('id', 'file', 'comment__text',) 
admin.site.register(Evidence, EvidenceAdmin)

class GeneAdmin(admin.ModelAdmin):
    list_display = ('name', 'inheritance_pattern', 'conditions',)
    search_fields = ('name', 'inheritance_pattern', 'conditions',)
admin.site.register(Gene, GeneAdmin)

class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sample_name_only', 'worklist', 'affected_with', 'analysis_performed', 'other_changes',)
    search_fields = ('id', 'name', 'sample_name_only', 'worklist__name', 'affected_with', 'analysis_performed__panel', 'other_changes',)
admin.site.register(Sample, SampleAdmin)

class TranscriptVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant', 'transcript', 'hgvs_c', 'hgvs_p', 'exon', 'consequence',)
    search_fields = ('id', 'transcript__name', 'hgvs_c', 'hgvs_p', 'exon', 'consequence',)
admin.site.register(TranscriptVariant, TranscriptVariantAdmin)

class TranscriptAdmin(admin.ModelAdmin):
    list_display = ('name', 'gene',)
    search_fields = ('name', 'gene__name',)
admin.site.register(Transcript, TranscriptAdmin)

class UserCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'classification', 'user', 'text', 'time', 'visible',)
    search_fields = ('id', 'classification__id', 'user__username', 'text', 'time', 'visible',)
admin.site.register(UserComment, UserCommentAdmin)

class VariantAdmin(admin.ModelAdmin):
    list_display = ('chromosome', 'position', 'ref', 'alt', 'variant_hash',)
    search_fields = ('variant_hash', 'chromosome', 'position', 'ref', 'alt',)
admin.site.register(Variant, VariantAdmin)

class WorklistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
admin.site.register(Worklist, WorklistAdmin)

class PanelAdmin(admin.ModelAdmin):
    list_display = ('panel', 'added_by',)
    search_fields = ('panel', 'added_by',)
admin.site.register(Panel, PanelAdmin)

class CNVSampleAdmin(admin.ModelAdmin):
	list_display = ('id','sample_name','worklist',)
	search_fields = ('id','sample_name','worklist',)
admin.site.register(CNVSample, CNVSampleAdmin)
