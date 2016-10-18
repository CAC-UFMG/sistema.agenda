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
from plone.namedfile import field as namedfile
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

tipoEspaco = SimpleVocabulary.fromValues(['Auditorio','Hall','Laboratorio','Sala de aula','Sala administrativa','Saguao'])

# Interface class; used to define content-type schema.

class Ilocal(form.Schema, IImageScaleTraversable):
    """
    Localizacao do evento
    """

    title = schema.TextLine(title=_(u"Nome do local"))
    fotopalco = namedfile.NamedBlobImage(title=_(u"Foto do palco"), required=False)
    fotoplateia = namedfile.NamedBlobImage(title=_(u"Foto da plateia"), required=False)
    bloco = schema.TextLine(title=_(u"Bloco"),required=False)
    andar = schema.TextLine(title=_(u"Andar"),required=False)
    unidade = schema.TextLine(title=_(u"Unidade"))
    altura = schema.TextLine(title=_(u"Altura do palco"),required=False)
    largura = schema.TextLine(title=_(u"Largura do palco"),required=False)
    profundidade = schema.TextLine(title=_(u"Profundidade do palco"),required=False)
    tipo = schema.Choice(title=u"Tipo",required=True,vocabulary=tipoEspaco)
    capacidadeTotal = schema.TextLine(title=_(u"Capacidade total"),required=False)
	
    form.fieldset('capacidade',label=u"Publico especial", fields=['capacidadeCadeirantes','capacidadeObesos'])    
    capacidadeCadeirantes = schema.TextLine(title=_(u"Cadeirantes"),required=False)
    capacidadeObesos = schema.TextLine(title=_(u"Obesos"),required=False)


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
            di=datetime(obj.start.year,obj.start.month,obj.start.day)
            df=datetime(obj.end.year,obj.end.month,obj.end.day)
            if df>=hoje:
              result.append(obj)
     result=sorted(result,key=lambda evnt:evnt.start)
     return result
	 
    def equipamentosNesseLocal(self):
     source_object = self.context
     result = []
     for rel in source_object.listFolderContents():        
        if rel is not None and checkPermission('zope2.View', rel):
            result.append(rel)
     return result


