from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Item, Container

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile import field as namedfile

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from datetime import datetime
import random
from sistema.agenda import MessageFactory as _


# Interface class; used to define content-type schema.
permissaoAdm='sistema.agenda.modificaRecurso'
class Ijustificativa(form.Schema, IImageScaleTraversable):
    """
    Membro de equipe tecnica
    """
	#form.write_permission(equipe=permissaoAdm)
    #form.write_permission(categoria=permissaoAdm)
	
    title = schema.TextLine(title=_(u"Titulo da justificativa"))
    id=schema.TextLine(title=u"Numero identificador")	
    data = schema.Date(title=u'Data do dia justificado')   
    texto=schema.Text(title=u"Justificativa")	
    anexoA= namedfile.NamedBlobFile(title=_(u"Documento anexo A"), required=False)
    anexoB= namedfile.NamedBlobFile(title=_(u"Documento anexo B"), required=False)


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
@form.default_value(field=Ijustificativa['id'])
def idDefault(data):      
    return  random.getrandbits(64)
	
class justificativa(Item):
    grok.implements(Ijustificativa)

    # Add your class methods and properties here
    pass


# View class
# The view will automatically use a similarly named template in
# membrodeequipe_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(dexterity.DisplayForm):
    """ sample view class """

    grok.context(Ijustificativa)
    grok.require('zope2.View')

    pass
