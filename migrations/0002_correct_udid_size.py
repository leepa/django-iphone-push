
from south.db import db
from django.db import models
from iphonepush.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'iPhone.udid'
        db.alter_column('iphonepush_iphone', 'udid', models.CharField(max_length=64, blank=False))
        
    
    
    def backwards(self, orm):
        
        # Changing field 'iPhone.udid'
        db.alter_column('iphonepush_iphone', 'udid', models.CharField(max_length=40, blank=False))
        
    
    
    models = {
        'iphonepush.iphone': {
            'failed_phone': ('models.BooleanField', [], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'last_notified_at': ('models.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'notes': ('models.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'test_phone': ('models.BooleanField', [], {'default': 'False'}),
            'udid': ('models.CharField', [], {'max_length': '64', 'blank': 'False'})
        }
    }
    
    complete_apps = ['iphonepush']
