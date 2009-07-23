"""
django-iphone-push - Django Application for doing iPhone Push
Written by Lee Packham
http://leenux.org.uk/
http://github.com/leepa

(c)2009 Lee Packham - ALL RIGHTS RESERVED
May not be used for commercial applications without prior concent.
"""

from django.db import models
from django.conf import settings

from socket import socket

import datetime
import struct
import ssl
import binascii

# Handle Python 2.5 / 2.6 seamlessly
try:
    import json
except ImportError:
    import simplejson as json

class iPhone(models.Model):
    """
    Represents an iPhone used to push
    
    udid - the iPhone Unique Push Identifier (64 chars of hex)
    last_notified_at - when was a notification last sent to the phone
    test_phone - is this a phone that should be included in test runs
    notes - just a small notes field so that we can put in things like "Lee's iPhone"
    failed_phone - Have we had feedback about this phone? If so, flag it.
    """
    udid = models.CharField(blank=False, max_length=64)
    last_notified_at = models.DateTimeField(blank=True, default=datetime.datetime.now)
    test_phone = models.BooleanField(default=False)
    notes = models.CharField(blank=True, max_length=100)
    failed_phone = models.BooleanField(default=False)
    
    class Admin:
        list_display = ('',)
        search_fields = ('',)
    
    def _getApnHostName(self):
        """
        Get the relevant hostname for the instance of the phone
        """
        if self.test_phone:
            return settings.IPHONE_SANDBOX_APN_HOST
        else:
            return settings.IPHONE_LIVE_APN_HOST
            
    def _getApnCertPath(self):
        """
        Get the relevant certificate for the instance of the phone
        """
        if self.test_phone:
            return settings.IPHONE_SANDBOX_APN_PUSH_CERT
        else:
            return settings.IPHONE_LIVE_APN_PUSH_CERT
    
    def send_message(self, alert, badge=0, sound="chime", 
                        custom_params={}, action_loc_key=None, loc_key=None,
                        loc_args=[], passed_socket=None):
        """
        Send a message to an iPhone using the APN server, returns whether
        it was successful or not.
        
        alert - The message you want to send
        badge - Numeric badge number you wish to show, 0 will clear it
        sound - chime is shorter than default! Replace with None/"" for no sound
        sandbox - Are you sending to the sandbox or the live server
        custom_params - A dict of custom params you want to send
        action_loc_key - As per APN docs
        loc_key - As per APN docs
        loc_args - As per APN docs, make sure you use a list
        passed_socket - Rather than open/close a socket, use an already open one
        
        See http://developer.apple.com/iphone/library/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/ApplePushService/ApplePushService.html
        """
        aps_payload = {}

        alert_payload = alert
        if action_loc_key or loc_key or loc_args:
            alert_payload = {'body' : alert}
            if action_loc_key:
                alert_payload['action-loc-key'] = action_loc_key
            if loc_key:
                alert_payload['loc-key'] = loc_key
            if loc_args:
                alert_payload['loc-args'] = loc_args

        aps_payload['alert'] = alert_payload
        
        if badge:
            aps_payload['badge'] = badge
        
        if sound:
            aps_payload['sound'] = sound        
        
        payload = custom_params
        payload['aps'] = aps_payload
        
        # This ensures that we strip any whitespace to fit in the 
        # 256 bytes
        s_payload = json.dumps(payload, separators=(',',':'))
        
        # Check we're not oversized
        if len(s_payload) > 256:
            raise OverflowError, 'The JSON generated is too big at %d - *** "%s" ***' % (len(s_payload), s_payload)

        fmt = "!cH32sH%ds" % len(s_payload)
        command = '\x00'
        msg = struct.pack(fmt, command, 32, binascii.unhexlify(self.udid), len(s_payload), s_payload)
        
        if passed_socket:
            passed_socket.write(msg)
        else:
            s = socket()
            c = ssl.wrap_socket(s,
                                ssl_version=ssl.PROTOCOL_SSLv3,
                                certfile=self._getApnCertPath())
            c.connect((self._getApnHostName(), 2195))
            c.write(msg)
            c.close()
        
        return True

    def __unicode__(self):
        return u"iPhone %s" % self.udid
        
def sendMessageToPhoneGroup(phone_list, alert, badge=0, sound="chime", 
                            custom_params={}, action_loc_key=None, loc_key=None,
                            loc_args=[], sandbox=False):
    """
    See the syntax for send_message, the only difference is this opens
    one socket to send them all.
    
    The caller must ensure that all phones are the same sandbox level
    otherwise it'll end up sending messages to the wrong service.
    """
    host_name = None
    cert_path = None
    
    if sandbox:
        host_name = settings.IPHONE_SANDBOX_APN_HOST
        cert_path = settings.IPHONE_SANDBOX_APN_PUSH_CERT
    else:
        host_name = settings.IPHONE_LIVE_APN_HOST
        cert_path = settings.IPHONE_LIVE_APN_PUSH_CERT
    
    s = socket()
    c = ssl.wrap_socket(s,
                        ssl_version=ssl.PROTOCOL_SSLv3,
                        certfile=cert_path)
    c.connect((host_name, 2195))
    
    for phone in phone_list:
        if phone.test_phone == sandbox:
            phone.send_message(alert, badge, sound, custom_params,
                            action_loc_key, loc_key, loc_args, c)
    
    c.close()
    
def doFeedbackLoop(sandbox = False):
    """
    Contact the APN server and ask for feedback on things that
    have not gone through so the iPhone list can be updated accordingly
    
    Does two things:
        1. Find all associated iPhone objects and set failed_device to True
        2. Return a dict of hexlified push IDs with the time_t
        
    Annoyingly, I've had to stub this out for now as it seems that sandbox
    feedback service just doesn't do anything at all!
    
    If Apple fix that, I can test/debug a lot easier. Until then...
    """
    raise NotImplementedError
    
    if sandbox:
        host_name = settings.IPHONE_SANDBOX_FEEDBACK_HOST
        cert_path = settings.IPHONE_SANDBOX_APN_PUSH_CERT
    else:
        host_name = settings.IPHONE_LIVE_FEEDBACK_HOST
        cert_path = settings.IPHONE_LIVE_APN_PUSH_CERT

    s = socket()
    c = ssl.wrap_socket(s,
                        ssl_version=ssl.PROTOCOL_SSLv3,
                        certfile=settings.IPHONE_APN_PUSH_CERT)
    c.connect((settings.IPHONE_FEEDBACK_HOST, 2196))

    full_buf = ''
    while 1:
        tmp = c.recv(38)
        print tmp
        if not tmp:
            break
        else:
            full_buf += tmp
        
    c.close()
