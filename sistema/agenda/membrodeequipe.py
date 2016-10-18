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
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from Products.CMFCore.utils import getToolByName

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from datetime import datetime

from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid

from sistema.agenda import MessageFactory as _

def loginValidation(data):
	
	if len(data)<=4:
		raise Invalid(u'Login invalido')
	return True
	
def senhaValidation(data):

    if len(data)<=8:
      raise Invalid(u'Senha invalida')
    return True
	
def validateaddress(data):
    try:
        checkEmailAddress(data)
    except EmailAddressInvalid:
    	  raise Invalid(u"XXXX@XXX.XXX")
    return True
	
# Interface class; used to define content-type schema.
permissaoAdm='sistema.agenda.modificaRecurso'
class ImembroDeEquipe(form.Schema, IImageScaleTraversable):
    """
    Membro de equipe tecnica
    """
    form.fieldset('dpessoais',label=u"Dados Pessoais", fields=['title','email','funcao','regime'])
    title = schema.TextLine(title=_(u"Nome do membro"))
    login = schema.TextLine(title=_(u'Login'), required=True,constraint=loginValidation)
    senha = schema.Password(title=_(u'Senha'), required=True,constraint=senhaValidation)
    loginAntigo = schema.TextLine(title=_(u'Login Anterior'), readonly=True)
    email = schema.TextLine(title=_(u'Email'), constraint=validateaddress,required=True)
    funcao = schema.TextLine(title=_(u"Funcao"),required=False)
    regime = schema.TextLine(title=_(u"Regime"),required=False)   


@grok.subscribe(ImembroDeEquipe, IObjectAddedEvent)
def adicionaUsr(membro, event):
  membro.title=membro.title.title() 
  membro.login=membro.login.lower()

  regTool = getToolByName(membro, 'portal_registration')
  portal_url = getToolByName(membro, 'portal_url')
  portal = portal_url.getPortalObject()
  mt = getToolByName(portal, 'portal_membership')
  senha = str(membro.senha)
  if mt.getMemberById(membro.login) is None:
    login= str(membro.login).lower()
  else:
    raise  schema.ValidationError('Login existente!')
    return
  
  prop = {
        'username': login ,
        'fullname': membro.title,
        'email': membro.email or ''
        }

  member =  regTool.addMember(login,senha,properties=prop,roles=('Member',))
  membro.loginAntigo=login
  membro.manage_setLocalRoles(login, ["Owner",])
  membro.reindexObjectSecurity()
 
@grok.subscribe(ImembroDeEquipe, IObjectRemovedEvent)
def removeUsr(membro, event):
  regTool = getToolByName(membro, 'portal_membership')
  portal_url = getToolByName(membro, 'portal_url')
  portal = portal_url.getPortalObject()
  mt = getToolByName(portal, 'portal_membership')
  login= str(membro.login).lower()
  if mt.getMemberById(login) is not None:
    regTool.deleteMembers([login])


@grok.subscribe(ImembroDeEquipe, IObjectModifiedEvent)
def atualizaCampos(membro, event):
  portal_url = getToolByName(membro, 'portal_url')
  portal = portal_url.getPortalObject()
  mt = getToolByName(portal, 'portal_membership')
  regTool = getToolByName(membro, 'portal_registration')
  login= str(membro.login).lower()
  loginAntigo= str(membro.loginAntigo)
  senha = str(membro.senha)
  if mt.getMemberById(login) is not None and login!=loginAntigo:
    # se ja houver um membro com o login,lanca erro
    raise  schema.ValidationError('Login existente!')
    return
  else:
       if login!=loginAntigo:
           mt.deleteMembers([loginAntigo])
           membro.loginAntigo=login
           prop = {'username': login,'fullname': membro.title,'email': membro.email or ''} 
           regTool.addMember(login,senha,properties=prop,roles=('Member',))
           membro.manage_setLocalRoles(login, ["Owner",])
           membro.reindexObjectSecurity()
           #groups_tool = getToolByName(portal, 'portal_groups')

class membroDeEquipe(Container):
    grok.implements(ImembroDeEquipe)

    # Add your class methods and properties here
    pass


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
            if df>=hoje:
              result.append(obj)
     result=sorted(result,key=lambda evnt:evnt.start)	
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