from django.contrib import admin

from .models import (
    UserAddress, UserBirthDate, UserLink, UserPhone, UserAvatar,
    UserEducation, UserProfile, UserWorkExperience, UserEmailStatus
)

@admin.register(UserEmailStatus)
class UserEmailStatusAdmin(admin.ModelAdmin):
    list_display = ("user", "created", "modified")
    search_fields = ("user__username", "user__email")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "created", "modified")
    list_filter = ("gender",)
    search_fields = ("user__username", "user__email")


@admin.register(UserBirthDate)
class UserBirthDateAdmin(admin.ModelAdmin):
    list_display = ("user", "birth_date", "created", "modified")
    search_fields = ("user__username",)
    list_filter = ("birth_date",)


@admin.register(UserLink)
class UserLinkAdmin(admin.ModelAdmin):
    list_display = ("user", "link", "created")
    search_fields = ("user__username", "link")


@admin.register(UserPhone)
class UserPhoneAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("user__username", "phone")


@admin.register(UserAvatar)
class UserAvatarAdmin(admin.ModelAdmin):
    list_display = ("user", "birth_date", "created")
    search_fields = ("user__username",)


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "country")
    list_filter = ("city", "country")
    search_fields = ("user__username",)


@admin.register(UserEducation)
class UserEducationAdmin(admin.ModelAdmin):
    list_display = ("user", "school", "degree", "field_of_study", "start_date", "end_date")
    list_filter = ("school", "degree", "field_of_study")
    search_fields = ("user__username", "school", "degree", "field_of_study")


@admin.register(UserWorkExperience)
class UserWorkExperienceAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "position", "start_date", "end_date")
    list_filter = ("company", "position")
    search_fields = ("user__username", "company", "position")
