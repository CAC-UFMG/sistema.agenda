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

tipoEspaco = SimpleVocabulary.fromValues(['Auditorio','Hall','Laboratorio','Sala de aula','Sala administrativa','Saguao'])

# Interface class; used to define content-type schema.

class Ilocal(form.Schema, IImageScaleTraversable):
    """
    Localizacao do evento
    """

    title = schema.TextLine(title=_(u"Nome do local"))
    bloco = schema.TextLine(title=_(u"Bloco"),required=False)
    andar = schema.TextLine(title=_(u"Andar"),required=False)
    unidade = schema.TextLine(title=_(u"Unidade"))
    tipo = schema.Choice(title=u"Tipo",required=True,vocabulary=tipoEspaco)
	
    form.fieldset('capacidade',label=u"Capacidade", fields=['capacidadeTotal','capacidadeCadeirantes','capacidadeObesos'])
    capacidadeTotal = schema.TextLine(title=_(u"Total"),required=False)
    capacidadeCadeirantes = schema.TextLine(title=_(u"Cadeirantes"),required=False)
    capacidadeObesos = schema.TextLine(title=_(u"Obesos"),required=False)

    form.fieldset('equipamentos',label=u"Equipamentos", fields=['arCondicionado','cabineDeTraducao','caixaDeSomPequena',
    'caixaDeRetorno','cameraDeVideoAutomatica','desktop','mesaDigitalizadora','microfoneComum','microfoneMesa','microfoneSemFio',
    'notebook','projetor','telaInterativa','televisor'])
    arCondicionado = schema.Bool(title=_(u"Ar-condicionado"),required=False)
    cabineDeTraducao = schema.TextLine(title=_(u"Cabine de traducao"),required=False)
    caixaDeSomPequena = schema.TextLine(title=_(u"Caixa de som pequena"),required=False)
    caixaDeRetorno = schema.TextLine(title=_(u"Caixa de retorno"),required=False)
    cameraDeVideoAutomatica	= schema.TextLine(title=_(u"Camera de video automatica"),required=False)
    desktop = schema.TextLine(title=_(u"Computador desktop para usuarios"),required=False)
    mesaDigitalizadora = schema.TextLine(title=_(u"Mesa digitalizadora"),required=False)
    microfoneComum = schema.TextLine(title=_(u"Microfone comum"),required=False)
    microfoneMesa = schema.TextLine(title=_(u"Microfone de mesa"),required=False)
    microfoneSemFio = schema.TextLine(title=_(u"Microfone sem fio"),required=False)
    notebook = schema.TextLine(title=_(u"Notebook"),required=False)
    projetor = schema.TextLine(title=_(u"Projetor"),required=False)
    telaInterativa = schema.TextLine(title=_(u"Tela interativa"),required=False)
    televisor = schema.TextLine(title=_(u"Televisor"),required=False)

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class local(Item):
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
            result.append(obj)
     return result


