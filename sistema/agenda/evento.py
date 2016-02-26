# -*- coding: utf-8 -*-

from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import random

from plone.dexterity.content import Item

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from datetime import datetime,date,time
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.relationfield.schema import RelationChoice, RelationList
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget,CheckBoxFieldWidget
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI
from zope.schema import getFieldsInOrder
from z3c.relationfield.relation import RelationValue

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
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFCore.utils import getToolByName
from zope.lifecycleevent import modified
from plone.uuid.interfaces import IUUID

listaDeCategorias = SimpleVocabulary.fromValues(['Interno','Externo'])
sortTiposEvento = ['Aula','Defesa',u'Colacao','Formatura',u'Seminario',
'Palestra',u'Forum',u'Simposio','Mostra','Congresso','Encontro','Ensaio','Montagem',u'Manutencao',
u'Capacitacao','Workshop','Prova',u'Recepcao','Solenidade','Festividade',u'Reuniao']
sortTiposEvento.sort()
tiposEvento = SimpleVocabulary.fromValues(sortTiposEvento)
listaServicosExtras = SimpleVocabulary.fromValues(['Rede WiFi','Transmissao interna','Transmissao via internet','Traducao simultanea',])

def telefoneValidation(data):
	tel = data.replace("(","")
	tel = tel.replace(")","")
	tel = tel.replace("-","")
	tel = tel.replace(" ","")
	if not tel.isdigit() or len(data)<7 or data[-5]!= "-" or data[0]!="(" or data[3]!=")" or data.count(" ")>0:
	 	raise Invalid(_(u"O número deve ser no formato (XX)XXXXX-XXXX"))
	return True
	
	
def validateaddress(data):
    try:
        checkEmailAddress(data)
    except EmailAddressInvalid:
    	  raise Invalid(u"XXXX@XXX.XXX ")
    return True	
	
def publicoValidation(data):
    try:
        int(data) 
    except ValueError:
    	  raise Invalid(u'Informe somente números')
    return True		

def cpfValidation(data):
	d1=0
	d2=0
	i=0
	if len(data)!=11:
            raise Invalid(_(u"CPF Inválido"))
        else:
            while i<10:
		d1,d2,i=(d1+(int(data[i])*(11-i-1)))%11 if i<9 else d1,(d2+(int(data[i])*(11-i)))%11,i+1
	    resultado=(int(data[9])==(11-d1 if d1>1 else 0)) and (int(data[10])==(11-d2 if d2>1 else 0))
	    if not resultado:
		raise Invalid(_(u"CPF Inválido"))
	return True


 
@grok.provider(IContextSourceBinder)
def pastaLocais(context):
    portal_url = getToolByName(context,'portal_url')
    siteId = portal_url.getPortalObject().id
    path = '/'+siteId+'/locais'
    query = { "object_provides" : Ilocal.__identifier__, "path":{'query':path}}

    return ObjPathSourceBinder(navigation_tree_query = query).__call__(context) 
	
	
@grok.provider(IContextSourceBinder)
def pastaEquipe(context):
    portal_url = getToolByName(context,'portal_url')
    siteId = portal_url.getPortalObject().id
    path = '/'+siteId+'/equipe'
    query = { "object_provides" : ImembroDeEquipe.__identifier__, "path":{'query':path}}

    return ObjPathSourceBinder(navigation_tree_query = query).__call__(context) 	


permissaoAdm='sistema.agenda.visualizaEvento'
class Ievento(form.Schema, IImageScaleTraversable):
    """
    Evento
    """
    form.write_permission(equipe=permissaoAdm)
    form.write_permission(categoria=permissaoAdm)    
	
    id=schema.TextLine(title=u"Número identificador desta solicitação.",description=u'NÃO MODIFICAR. Anote este número.')	
    categoria=schema.Choice(title=u"Categoria",description=u'PARA O AGENDADOR: Informe se o evento é da UFMG (interno) ou não (externo)',required=False,vocabulary=listaDeCategorias)
    tipo=schema.Choice(title=u"Tipo",required=True,vocabulary=tiposEvento)	
    local=RelationList(title=u"Local",description=u'Escolha os espaços a serem agendados',required=True,value_type=RelationChoice(title=u'Local',required=True,source=pastaLocais))
    equipe=RelationList(title=u"Equipe",description=u'PARA O AGENDADOR: Informe a equipe para este evento',required=False,value_type=RelationChoice(title=u'Equipe',required=True,source=pastaEquipe))	
    previsaoDePublico=schema.TextLine(title=u"Previsão de Público",description=u'Informe a previsão do número de participantes',required=True,constraint=publicoValidation)
    servicosExtras=schema.Set(title=u"Serviços Extras",description=u'O evento necessita de algum destes serviços?',required=False, value_type=schema.Choice(source=listaServicosExtras))
    form.widget('servicosExtras', CheckBoxFieldWidget)
	
    form.fieldset('dadosSolicitante',label=u"Dados do solicitante", fields=['responsavel','cpf','instituicao','unidade','telefone','email'] ) 
    responsavel=schema.TextLine(title=u"Responsável pelo evento",description=u'Indique o nome completo do responsável pelo evento.',required=True)
    instituicao=schema.TextLine(title=u"Instituição",description=u'Informe qual a instituição ligada ao evento',required=True,default=u'UFMG')
    unidade=schema.TextLine(title=u"Unidade",description=u'Informe a unidade ou departamento que está fazendo a solicitação',required=True)
    telefone=schema.TextLine(title=u"Telefone",description=u'Informe o contato telefônico do responsável pelo evento',required=True,constraint=telefoneValidation)
    email=schema.TextLine(title=u"E-mail",description=u'Informe o email do responsável pelo evento',required=True,constraint=validateaddress)
    cpf=schema.TextLine(title=u"CPF",constraint=cpfValidation, description=u'Informe o cpf do responsável pelo evento',required=True)
	
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



@form.default_value(field=Ievento['id'])
def idDefault(data):
    return random.getrandbits(64)
	
	
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
  if pai.id == 'agenda':
    clipboard = pai.manage_cutObjects([evento.id])
    dest = pai.get('preagenda')
    result = dest.manage_pasteObjects(clipboard)
    modified(result)
  enviaEmail(evento)
  
def enviaEmail(solicitacao):
	servidor = getToolByName(solicitacao,'MailHost')
	info = obtemTodasInformacoesDeConteudo(solicitacao)
	del info[solicitacao.id]['categoria']
	del info[solicitacao.id]['equipe']	
	mt = getToolByName(solicitacao,'portal_membership')
	emailAgendador = mt.getMemberById('agendador').email
	mensagem = "Solicitação de agendamento.\n\n"
	mensagem = mensagem + str('responsavel').upper()+" "+ str(info[solicitacao.id]['responsavel'])+"\n"    
	mensagem = mensagem + str('email').upper()+" "+ str(info[solicitacao.id]['email'])+"\n"    
	mensagem = mensagem + str('cpf').upper()+" "+ str(info[solicitacao.id]['cpf'])+"\n"    
	mensagem = mensagem + str('telefone').upper()+" "+ str(info[solicitacao.id]['telefone'])+"\n\n"    
	mensagem = mensagem + str('local solicitado').upper()+" "+ str(info[solicitacao.id]['local'])+"\n"    
	mensagem = mensagem + str("Data de começo ").upper()+ str(solicitacao.start.day)+'/'+str(solicitacao.start.month)+' de '+str(solicitacao.start.year)+' às '+str(solicitacao.start.hour)+' e '+str(solicitacao.start.minute)+"\n" 
	mensagem = mensagem + str("Data de término ").upper()+str(solicitacao.end.day)+'/'+str(solicitacao.end.month)+' de '+str(solicitacao.end.year)+' até '+str(solicitacao.end.hour)+' e '+str(solicitacao.end.minute)+"\n\n" 
	del info[solicitacao.id]['email']
	del info[solicitacao.id]['responsavel']
	del info[solicitacao.id]['local']
	del info[solicitacao.id]['cpf']
	del info[solicitacao.id]['telefone']
	
	lista=info[solicitacao.id].keys()
	for dado in lista:		
		mensagem = mensagem + str(dado).upper()+" "+ str(info[solicitacao.id][dado])+"\n"    
	mensagem = mensagem + "\n\n ESTES DADOS SERVEM PARA SUA CONFERÊNCIA. ESTA É UMA MENSAGEM AUTOMÁTICA. POR FAVOR NÃO RESPONDA A ESSE EMAIL."  
	emailsEnvolvidos = solicitacao.email+";"+emailAgendador
	titulo="Proposta de agendamento de "+solicitacao.responsavel
	emailConta = 'ti@prograg.ufmg.br'
	try:
		servidor.send(mensagem, emailsEnvolvidos,emailConta,titulo)
	except:
		pass
	return
	
def obtemTodasInformacoesDeConteudo(conteudo):
    intids = getUtility(IIntIds)
    tipo="sistema.agenda."+str(conteudo.Type())
    tipo=tipo.lower()
    schema = getUtility(IDexterityFTI, name=tipo).lookupSchema()
    campos=getFieldsInOrder(schema)    
    dados={}
    dados[conteudo.id]={}
    for campo,val in campos:
      valor =getattr(conteudo,campo)
      if valor is None:
          valor=''
      else:     
       #se o campo for relacional      
       if isinstance(valor,list): 
        if len(valor) and isinstance(valor[0], RelationValue):
         lista=valor
         valor=[]
         for educandoMatriculado in lista:
          at=getattr(educandoMatriculado,'to_id',None)
          if at:
           obj = intids.queryObject(at)
           valor.append(obj.title)
       #se o campo nao for do tipo relacao
       else:
        #se o campo for executavel
        if valor is callable:
          valor=valor()
        else:
            #se o campo for string
            if isinstance(valor,str):
              valor=valor
              #para acentuacao usar valor.decode('iso-8859-1')             
            # se o campo for data
            if isinstance(valor,date):
              valor=str(valor)
		
      idCampo = campo      
      if isinstance(valor,str):          
        valor=valor.decode('utf-8')
      if isinstance(valor,list):
        valor=str(valor)          
      if isinstance(valor,set):
        valor=str(valor)          
      if isinstance(valor,date):
        valor=str(valor)          
      if isinstance(valor,time):
        valor=str(valor)      
      if valor is callable:
        valor=valor()                    
      if isinstance(valor,bool):
        valor=str(valor)
      if isinstance(valor,NamedBlobImage) or isinstance(valor,NamedBlobFile):
        valor='arquivo' 
      dados[conteudo.id][idCampo]= valor        
    
    return dados
  

class evento(Item):
    grok.implements(Ievento)

 
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