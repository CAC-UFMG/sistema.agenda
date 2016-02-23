# -*- coding: utf-8 -*-
from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Item,Container

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from datetime import datetime

from sistema.agenda import MessageFactory as _


# Interface class; used to define content-type schema.

class Ilocal(form.Schema, IImageScaleTraversable):
    """
    Localizacao do evento
    """

    title = schema.TextLine(title=_(u"Nome do local"))
    unidade = schema.TextLine(title=_(u"Unidade"))	


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class local(Container):
    grok.implements(Ilocal)

    # Add your class methods and properties here
    pass


# View class
# The view will automatically use a similarly named template in
# local_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(dexterity.DisplayForm):
    """ sample view class """

    grok.context(Ilocal)
    grok.require('zope2.View')

    def eventoNesseLocal(self):
	
     catalog = getUtility(ICatalog)
     intids = getUtility(IIntIds)
     source_object = self.context
     result = []
     for rel in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='local')):
        obj = intids.queryObject(rel.from_id)
        if obj is not None and checkPermission('zope2.View', obj):
            dia=datetime.today()            
            hoje=datetime(dia.year,dia.month,dia.day)
            d=datetime(obj.start.year,obj.start.month,obj.start.day)
            if d>=hoje:
              result.append(obj)
     return result
	 
    def equipamentosNesseLocal(self):
     source_object = self.context
     result = []
     for rel in source_object.listFolderContents():        
        if rel is not None and checkPermission('zope2.View', rel):
            result.append(rel)
     return result


