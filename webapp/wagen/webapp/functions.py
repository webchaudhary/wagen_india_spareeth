#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 23:27:45 2021

@author: lucadelu
"""
import os
import time
from datetime import date
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
import jinja2
from weasyprint import HTML

def send_mail_attach(sub, mess, to, attach):
    """Send email with attachment"""
    try:
        email = EmailMessage(
            sub,
            mess,
            settings.EMAIL_ADDR,
            [to],
        )
        email.attach_file(attach)
        email.send()
    except Exception as e:
        if e[0] == 551 and 'message sending quota exceeded' in e[1]:
            time.sleep(120)
            send_mail_attach(sub, mess, to, attach)
        else:

            return {"result": "There was an error sending email to {}".format(to),
                    "error": e}
    return True


def get_date():
    "Get today's date in German format"
    today = date.today()
    return today.strftime("%Y-%m-%d")

def render_html(jobid, area):
    """Render html page using jinja"""
    template_loader = jinja2.FileSystemLoader(searchpath=os.path.join(settings.BASE_DIR, 'webapp', "templates"))
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "report.html"
    template = template_env.get_template(template_file)
    output_text = template.render(area=area.name, settings=settings, job=jobid)
    html_path = os.path.join(settings.MEDIA_ROOT, jobid, 'index.html')
    with open(html_path, 'w') as html_file:
        html_file.write(output_text)
    return html_path

def render_prod_html(jobid, area, stats):
    """Render html page using jinja"""
    template_loader = jinja2.FileSystemLoader(searchpath=os.path.join(settings.BASE_DIR, 'webapp', "templates"))
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "report_custom_wb.html"
    template = template_env.get_template(template_file)
    output_text = template.render(area=area.name, settings=settings, job=jobid, stats=stats)
    html_path = os.path.join(settings.MEDIA_ROOT, jobid, 'index.html')
    with open(html_path, 'w') as html_file:
        html_file.write(output_text)
    return html_path

def render_pdf(html, jobid):
    """Render pdf page from html using weasyprint"""
    with open(html) as inhtml:
        htmlstr = inhtml.read()
    # replace img to embed because they work really better in weasyprint
    htmlstr = htmlstr.replace("img", "embed")
    
    mystatic = "{ut}://{ba}{st}".format(ut=settings.HTTP_TYPE,
                                        ba=Site.objects.get_current().domain,
                                        st=os.path.join(settings.STATIC_URL))
    mymedia = "{ut}://{ba}{me}".format(ut=settings.HTTP_TYPE,
                                       ba=Site.objects.get_current().domain,
                                       me=os.path.join(settings.MEDIA_URL))
    htmlstr = htmlstr.replace("/static/", mystatic)
    htmlstr = htmlstr.replace("/media/", mymedia)
    with open("{}.new".format(html), 'w') as outhtml:
        outhtml.write(htmlstr)
    pdf = HTML(string=htmlstr).write_pdf()
    pdf_path = os.path.join(settings.MEDIA_ROOT, jobid, 'report.pdf')
    with open(pdf_path, 'wb') as pdf_file:
        pdf_file.write(pdf)
    return pdf_path
    
