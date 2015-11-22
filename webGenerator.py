#!/usr/bin/python
# -*- coding: UTF-8 -*-

import html

doc = html.HTML()

doc.p(u'שבת שלום')



out = open('web.html','w')

out.write(unicode(doc))

out.close()