from django.contrib import admin

import stats.models as m


# Register your models here.


class WeaponType_admin(admin.ModelAdmin):
    # list_display = ("name", "size", "has_ammo_B",)
    exclude = (
        "translated_title",
        "core_gun",
        "size",
        "sights",
        "melee",
        "muzzle",
        "weight",
        "price",
    )


class Layout_admin(admin.ModelAdmin):
    list_display = (
        "primary_type",
        "secondary_type",
        "layout_type",
    )


admin.site.register(m.WeaponType, WeaponType_admin)
admin.site.register(m.Weapon)
admin.site.register(m.Layout, Layout_admin)
admin.site.register(m.Slots)
