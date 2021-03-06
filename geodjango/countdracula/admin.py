import logging, os, traceback
from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from django.contrib.gis.maps.google import GoogleMap
from django.shortcuts import render

from countdracula.forms import UploadCountForm
from countdracula.models import Node,StreetName,TurnCountLocation,TurnCount,MainlineCountLocation,MainlineCount

# key associated with sfcta.mapping@gmail.com
GMAP = GoogleMap(key='AIzaSyDSscDrdYK3lENjefyjoBof_JjXY5LJLRo')

# create custom admin site to add the upload counts view
class CountDraculaAdminSite(admin.sites.AdminSite):
    
    def get_urls(self):
        urls = super(CountDraculaAdminSite, self).get_urls()
        my_urls = patterns('', (r'^upload_counts/$', self.admin_view(self.upload_view)))
        # print "CountDraculaAdminSite"
        # print (my_urls + urls)
        # todo: can we put the auth (admin.site.get_urls() here?  it'd be nice to have one page)
        return my_urls + urls
    
    def upload_view(self, request):
        context_dict = {}
        
        if request.method == 'POST':
            form = UploadCountForm(request.POST, request.FILES)
            if form.is_valid():
                (num_processed, log_string) = form.read_sourcefile_and_insert_counts(request, request.FILES['sourcefile'])
                if num_processed < 0:
                    context_dict['upload_errors'] = log_string
                else:
                    # success!
                    context_dict['success_msg'] = "Successfully uploaded %d counts from %s!" % (num_processed, form.cleaned_data['sourcefile'])
                    context_dict['success_detail'] = log_string
                    form = UploadCountForm()
        else:
            # form is not bound to data
            form = UploadCountForm()

        context_dict['form'] = form
        return render(request, 'admin/countdracula/upload.html', context_dict)
        

countdracula_admin = CountDraculaAdminSite(name='countdracula')

class StreetNameAdmin(admin.ModelAdmin):
    search_fields = ['street_name']
    
    readonly_fields = ('nodes_map',)
    
    def nodes_map(self, instance):
        return '<pre>' + (str(instance.nodes.all())) + "</pre>"
    nodes_map.short_description = "Nodes Map"
    nodes_map.allow_tags = True
countdracula_admin.register(StreetName, StreetNameAdmin)

countdracula_admin.register(TurnCountLocation)

class MainlineCountInline(admin.TabularInline):
    model = MainlineCount
    
    readonly_fields = ('count','count_date','count_year',
                       'start_time','period_minutes','vehicle_type',
                       'sourcefile','project','reference_position','upload_user',)
    
    
class MainlineCountLocationAdmin(admin.ModelAdmin):
    list_display = ('on_street', 'from_street', 'to_street')

    inlines = [ MainlineCountInline, ]
    
countdracula_admin.register(MainlineCountLocation, MainlineCountLocationAdmin)
    
class TurnCountAdmin(admin.ModelAdmin):
    # let users search by sourcefile
    search_fields = ['sourcefile']
    list_filter   = ('vehicle_type',)
    list_display  = ('location', 'period_minutes', 'count_date', 'count_year', 'start_time', 'vehicle_type', 'count')
    
countdracula_admin.register(TurnCount, TurnCountAdmin)

class MainlineCountAdmin(admin.ModelAdmin):
    # let users search by sourcefile
    search_fields = ['sourcefile']
    list_filter   = ('vehicle_type',)
    list_display  = ('location', 'period_minutes', 'count_date', 'count_year', 'start_time', 'vehicle_type', 'count')

countdracula_admin.register(MainlineCount, MainlineCountAdmin)

class StreetnameInline(admin.TabularInline):
    model = StreetName.nodes.through
    
class NodeAdmin(gis_admin.OSMGeoAdmin):
    extra_js = [GMAP.api_url + GMAP.key]
    map_template = 'gis/admin/googlemap.html'
    
    inlines = [ StreetnameInline, ]
    
countdracula_admin.register(Node, NodeAdmin)
