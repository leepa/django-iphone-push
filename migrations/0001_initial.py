
from south.db import db
from django.db import models
from iphonepush.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'iPhone'
        db.create_table('iphonepush_iphone', (
            ('failed_phone', models.BooleanField(default=False)),
            ('udid', models.CharField(max_length=40, blank=False)),
            ('last_notified_at', models.DateTimeField(default=datetime.datetime.now, blank=True)),
            ('notes', models.CharField(max_length=100, blank=True)),
            ('test_phone', models.BooleanField(default=False)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('iphonepush', ['iPhone'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'iPhone'
        db.delete_table('iphonepush_iphone')
        
    
    
    models = {
        'iphonepush.iphone': {
            'failed_phone': ('models.BooleanField', [], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'last_notified_at': ('models.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'notes': ('models.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'test_phone': ('models.BooleanField', [], {'default': 'False'}),
            'udid': ('models.CharField', [], {'max_length': '40', 'blank': 'False'})
        }
    }
    
    complete_apps = ['iphonepush']
