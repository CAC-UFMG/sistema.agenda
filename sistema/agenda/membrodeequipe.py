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

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from datetime import datetime

from sistema.agenda import MessageFactory as _


# Interface class; used to define content-type schema.
permissaoAdm='sistema.agenda.modificaRecurso'
class ImembroDeEquipe(form.Schema, IImageScaleTraversable):
    """
    Membro de equipe tecnica
    """
	
    title = schema.TextLine(title=_(u"Nome do membro"))
    funcao = schema.TextLine(title=_(u"Funcao"),required=False)
    regime = schema.TextLine(title=_(u"Regime"),required=False)   


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class membroDeEquipe(Container):
    grok.implements(ImembroDeEquipe)

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

    grok.context(ImembroDeEquipe)
    grok.require('zope2.View')

    def eventoNesseLocal(self):
     catalog = getUtility(ICatalog)
     intids = getUtility(IIntIds)
     source_object = self.context
     result = []
     for rel in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='equipe')):
        obj = intids.queryObject(rel.from_id)
        if obj is not None and checkPermission('zope2.View', obj):
            dia=datetime.today()            
            hoje=datetime(dia.year,dia.month,dia.day)
            di=datetime(obj.start.year,obj.start.month,obj.start.day)
            df=datetime(obj.end.year,obj.end.month,obj.end.day)
            if di>=hoje or df<=hoje:
              result.append(obj)
     return result

	 
    def sinteseJustificativas(self):     
     membro = self.context
     result = {}
     datasFuturas=0
     datasAteHoje=0
     justificativas=membro.listFolderContents()
     numeroTotal=len(justificativas)
     motivos={}
     numMotivos=0
     for justificativa in justificativas: 
       dia=datetime.today()            
       hoje=datetime(dia.year,dia.month,dia.day)
       dataJustificada=datetime(justificativa.data.year,justificativa.data.month,justificativa.data.day)            
       if dataJustificada>dia:
        datasFuturas+=1
       if dataJustificada<=dia:
        datasAteHoje+=1 
       for mot in justificativa.motivos:
         if not motivos.has_key(mot):
   	       motivos[mot]=1
         else:
           motivos[mot]+=1
         numMotivos+=1
		 
     for i in motivos.keys():
       if numMotivos:
         motivos[i]=str(round(float(motivos[i])/numMotivos,2)*100)+"%"
		
     result['datasAteHoje']=datasAteHoje
     result['datasFuturas']=datasFuturas
     result['motivos']=motivos
     return result
	 
    def listaJustificativas(self):     
     membro = self.context
     result = []
     for justificativa in membro.listFolderContents():
        if justificativa is not None and checkPermission('zope2.View', justificativa):            
            result.append(justificativa)
     return result