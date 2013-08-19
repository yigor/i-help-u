# encoding: utf-8
from django.contrib import admin
from vacancy.models import Organization, Vacancy, SocialLink, VacancyRespond


class SocialLinkInline(admin.TabularInline):
    model = SocialLink


class OrganizationAdmin(admin.ModelAdmin):
    inlines = (SocialLinkInline, )


class VacancyAdmin(admin.ModelAdmin):
    pass


class VacancyRespondAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'vacancy_id', 'organization', 'response_date', 'user', 'user_contacted', 'user_hired')
    readonly_fields = ('response_date', )
    ordering = ('-response_date', )

    def vacancy_id(self, obj):
        return obj.vacancy.id
    vacancy_id.short_description = u'ID вакансии'

    def organization(self, obj):
        return obj.vacancy.organization.title
    organization.short_description = u'Организация'

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Vacancy, VacancyAdmin)
admin.site.register(VacancyRespond, VacancyRespondAdmin)

