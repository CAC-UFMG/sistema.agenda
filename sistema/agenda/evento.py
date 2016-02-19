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
from z3c.relationfield.schema import RelationChoice, RelationList

from plone.formwidget.contenttree import ObjPathSourceBinder
from sistema.agenda.membrodeequipe import ImembroDeEquipe
from sistema.agenda.local import Ilocal
from sistema.agenda import MessageFactory as _
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.intid.interfaces import IIntIds
from zope.component import getUtility
from zc.relation.interfaces import ICatalog
from Acquisition import aq_inner, aq_parent
from zope.interface import invariant, Invalid
from Products.CMFCore.interfaces import ISiteRoot

listaDeCategorias = SimpleVocabulary.fromValues(['Interno','Externo'])
sortTiposEvento = ['Aula','Defesa',u'Colacao','Formatura',u'Seminario',
'Palestra',u'Forum',u'Simposio','Mostra','Congresso','Encontro','Ensaio','Montagem',u'Manutencao',
u'Capacitacao','Workshop','Prova',u'Recepcao','Solenidade','Festividade',u'Reuniao']
sortTiposEvento.sort()
tiposEvento = SimpleVocabulary.fromValues(sortTiposEvento)
listaServicosExtras = SimpleVocabulary.fromValues(['Rede WiFi','Transmissao interna','Transmissao via internet','Traducao simultanea',])

class Ievento(form.Schema, IImageScaleTraversable):
    """
    Evento
    """
    categoria=schema.Choice(title=u"Categoria",required=True,vocabulary=listaDeCategorias)
    tipo=schema.Choice(title=u"Tipo",required=True,vocabulary=tiposEvento)
	
    local=RelationList(title=u"Local",required=True,value_type=RelationChoice(title=u'Local',required=True,source=ObjPathSourceBinder(object_provides=Ilocal.__identifier__)))
    equipe=RelationList(title=u"Equipe",required=True,value_type=RelationChoice(title=u'Equipe',required=True,source=ObjPathSourceBinder(object_provides=ImembroDeEquipe.__identifier__)))
	
    previsaoDePublico=schema.TextLine(title=u"Previsão de Público",required=True)
    servicosExtras=schema.Set(title=u"Serviços Extras",value_type=schema.Choice(source=listaServicosExtras))
	
    form.fieldset('dadosSolicitante',label=u"Dados do solicitante", fields=['responsavel','instituicao','telefone','email'] ) 
    responsavel=schema.TextLine(title=u"Responsável",required=True)
    instituicao=schema.TextLine(title=u"Instituição",required=True,default=u'UFMG')
    unidade=schema.TextLine(title=u"Unidade",required=True)
    telefone=schema.TextLine(title=u"Telefone",required=True)
    email=schema.TextLine(title=u"E-mail",required=True)

@grok.subscribe(Ievento, IObjectModifiedEvent)
def modificaEvento(evento, event):
  #se houver outro evento na mesma data com o mesmo espaco.
  catalog = getUtility(ICatalog)
  intids = getUtility(IIntIds)
  if evento.local:
   for it in evento.local:
    local = getattr(it,'to_id',None)
    if local:
     objLocal = intids.queryObject(local)   
     source_object = objLocal
     result = []
     for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='local')):
        objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)
        if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id:
         if (evento.start >= objEventoCadastrado.start and evento.start <= objEventoCadastrado.end) or (evento.end <= objEventoCadastrado.end and evento.end >= objEventoCadastrado.start) or (evento.end >= objEventoCadastrado.end and evento.start <= objEventoCadastrado.start):
            raise Invalid("Conflito de horario com:" + objLocal.title+" entre os eventos: "+objEventoCadastrado.title+" e "+ evento.title)
  if evento.equipe:
   for it in evento.equipe:
    local = getattr(it,'to_id',None)
    if local:
     objLocal = intids.queryObject(local)   
     source_object = objLocal
     result = []
     for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='equipe')):
        objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)
        if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id:
         if (evento.start >= objEventoCadastrado.start and evento.start <= objEventoCadastrado.end) or (evento.end <= objEventoCadastrado.end and evento.end >= objEventoCadastrado.start) or (evento.end >= objEventoCadastrado.end and evento.start <= objEventoCadastrado.start):
            raise Invalid("Conflito de equipe com:" + objLocal.title+" entre os eventos: "+objEventoCadastrado.title+" e "+ evento.title)




@grok.subscribe(Ievento, IObjectAddedEvent)
def adicionaEvento(evento, event):
  #se houver outro evento na mesma data com o mesmo espaco.
  catalog = getUtility(ICatalog)
  intids = getUtility(IIntIds)
  if evento.local:
   for it in evento.local:
    local = getattr(it,'to_id',None)
    if local:
     objLocal = intids.queryObject(local)   
     source_object = objLocal
     result = []
     for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='local')):
        objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)
        if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id:
         if (evento.start >= objEventoCadastrado.start and evento.start <= objEventoCadastrado.end) or (evento.end <= objEventoCadastrado.end and evento.end >= objEventoCadastrado.start) or (evento.end >= objEventoCadastrado.end and evento.start <= objEventoCadastrado.start):
            raise Invalid("Conflito de horario com:" + objLocal.title+" entre os eventos: "+objEventoCadastrado.title+" e "+ evento.title)
  if evento.equipe:
   for it in evento.equipe:
    local = getattr(it,'to_id',None)
    if local:
     objLocal = intids.queryObject(local)   
     source_object = objLocal
     result = []
     for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='equipe')):
        objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)
        if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id:
         if (evento.start >= objEventoCadastrado.start and evento.start <= objEventoCadastrado.end) or (evento.end <= objEventoCadastrado.end and evento.end >= objEventoCadastrado.start) or (evento.end >= objEventoCadastrado.end and evento.start <= objEventoCadastrado.start):
            raise Invalid("Conflito de equipe com:" + objLocal.title+" entre os eventos: "+objEventoCadastrado.title+" e "+ evento.title)
  pai = aq_parent(aq_inner(evento))
  clipboard = pai.manage_cutObjects([evento.id])
  dest = pai.get('preagenda')
  result = dest.manage_pasteObjects(clipboard)
	
class evento(Item):
    grok.implements(Ievento)

    # Add your class methods and properties here
    pass


# View class
# The view will automatically use a similarly named template in
# evento_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class SampleView(grok.View):
    """ sample view class """

    grok.context(Ievento)
    grok.require('sistema.agenda.visualizaEvento')

    # grok.name('view')

    # Add view methods here