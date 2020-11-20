#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.shortcuts import render
import datetime
import urllib.parse
import urllib.request
import re

#GAN
def salo(request):
  url = "http://www.russianchurchlondon.org/calendar/"
  post = ""
  try:
    response = urllib.request.urlopen(url)
    encoding = response.info().get_param('charset', 'utf8')
    text = response.read().decode(encoding)
    re_post = re.compile(r'<span class="headerfast">(.*?)</span>')
    match = re.search(re_post, text)
    if (match):
      post = match[1]
  except:
    pass

  return render(request, 'salo/salo.html', {'post':post})  
