# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.security import checkPermission
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from z3c.relationfield.relation import RelationValue
from zope.intid.interfaces import IIntIds
from Products.CMFCore.interfaces import ISiteRoot
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget,CheckBoxFieldWidget

from plone.dexterity.interfaces import IDexterityFTI
from zope.schema import getFieldsInOrder

from zope.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog
from Acquisition import aq_inner, aq_parent

from Products.CMFPlone.utils import _createObjectByType
from five import grok
from plone.directives import form
from zope import schema
from z3c.form import button
from Products.statusmessages.interfaces import IStatusMessage

from datetime import datetime,time,date,timedelta
import time as time2
import random
import copy
import csv


class Idownload_agendamento_salas(form.Schema):
	""" Define form fields """	
	   
	info=schema.Text(title=u"Informacoes do processo")
	saida=schema.Text(title=u"Planilha CSV",description=u"Copie e cole este texto em um arquivo e salve como .CSV")

@form.default_value(field=Idownload_agendamento_salas['saida'])
def saidaDefaultValue(data):
	sdm = data.context.session_data_manager
	session = sdm.getSessionData(create=True)
	solucao=""
	if session.has_key('saida'):	
		solucao= str(session['saida']) or "Sem processamento."
		del session['saida']
	return solucao
	
@form.default_value(field=Idownload_agendamento_salas['info'])
def infoDefaultValue(data):
	sdm = data.context.session_data_manager
	session = sdm.getSessionData(create=True)
	solucao=""
	if session.has_key('info'):
		solucao= str(session['info']) or "Sem processamento."
		del session['info']
	return solucao
	 	
 
class download_agendamento_salas(form.SchemaForm):
    """ Define Form handling
    """
    grok.name('download_agendamento_salas')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = Idownload_agendamento_salas
    ignoreContext = True

    label = u"Agendamento de salas - exibição"
    description = u"Sistema para criação de matriz de horarios de aulas"

    