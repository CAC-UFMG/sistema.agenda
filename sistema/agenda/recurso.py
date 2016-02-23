# -*- coding: utf-8 -*-
from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Item

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

from sistema.agenda import MessageFactory as _


# Interface class; used to define content-type schema.

class Irecurso(form.Schema, IImageScaleTraversable):
    """
    Localizacao do evento
    """

    title = schema.TextLine(title=_(u"Nome do recurso"))
    tipo = schema.TextLine(title=_(u"Tipo"),description=u'Ex: microfone, projetor, computador')
    local = schema.TextLine(title=_(u"Local"))
    estado = schema.TextLine(title=_(u"Estado de uso"),default=u"Bom",description=u'Ex: Bom, Danificado, Em manutenção', required=True)
    patrimonio =schema.TextLine(title=_(u"Patrimônio"),required=True)


@form.default_value(field=Irecurso['local'])
def localDefault(data):
    return data.context.title

class recurso(Item):
    grok.implements(Irecurso)

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

    grok.context(Irecurso)
    grok.require('zope2.View')  


