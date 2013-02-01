#
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
#Copyright © 2011-2013 Greek Research and Technology Network (GRNET S.A.)

#Developed by Leonidas Poulopoulos (leopoul-at-noc-dot-grnet-dot-gr),
#GRNET NOC
#
#Permission to use, copy, modify, and/or distribute this software for any
#purpose with or without fee is hereby granted, provided that the above
#copyright notice and this permission notice appear in all copies.
#
#THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH REGARD
#TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
#FITNESS. IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
#CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
#DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
#ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
#SOFTWARE.
#
#!/usr/bin/python
from gevent import monkey; monkey.patch_all()
import os
import traceback
from django.core.handlers.wsgi import WSGIHandler
from django.core.signals import got_request_exception
from django.core.management import call_command

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

def exception_printer(sender, **kwargs):
    traceback.print_exc()

got_request_exception.connect(exception_printer)
call_command('syncdb')

application = WSGIHandler()
