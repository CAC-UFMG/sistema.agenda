# -*- coding: utf-8 -*-

from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from z3c.form.interfaces import ActionExecutionError, WidgetActionExecutionError
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import random
from plone.app.event.dx.behaviors import IEventBasic,IEventRecurrence
from pytz import timezone


from plone.dexterity.content import Item

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from datetime import datetime,date,time
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.relationfield.schema import RelationChoice, RelationList
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget,CheckBoxFieldWidget
from z3c.form.browser.radio import RadioWidget
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.WorkflowCore import WorkflowException
from plone.dexterity.interfaces import IDexterityFTI
from zope.schema import getFieldsInOrder
from z3c.relationfield.relation import RelationValue
from plone.event.interfaces import IEventAccessor
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

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
from plone.app.event.dx.behaviors import first_weekday_sun0
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides


opcaoEletrica=SimpleVocabulary.fromValues(['Temos a necessidade de auxilio da equipe de eletrica durante o evento','Nao Temos a necessidade de auxilio da equipe de eletrica durante o evento'])
opcaoSeguranca=SimpleVocabulary.fromValues(['Temos a necessidade de auxilio da seguranca durante o evento','Nao Temos a necessidade de auxilio da seguranca durante o evento'])
opcaoPaineis=SimpleVocabulary.fromValues(['Solicitamos a disponibilizacao de paineis expositores pretos para o evento','Nao Solicitamos a disponibilizacao de paineis expositores pretos para o evento'])
opcaoLimpeza=SimpleVocabulary.fromValues(['Solicitamos a limpeza previa do local do evento','Nao Solicitamos a limpeza previa do local do evento'])
opcaoServicoPrevio=SimpleVocabulary.fromValues(['Solicitamos a ordem de servico previa no local do evento','Nao Solicitamos a ordem de servico previa no local do evento'])	
opcaoBanheiro=SimpleVocabulary.fromValues(['Solicitamos a abertura dos banheiros durante o evento','Nao Solicitamos a abertura dos banheiros durante o evento'])	
listaDeCategorias = SimpleVocabulary.fromValues(['Interno','Externo'])
listaPrioridadeTransporte=SimpleVocabulary.fromValues(['Vermelho','Amarelo','Verde'])
opcoesEstado = SimpleVocabulary.fromValues(['NA','NAO ENVIADO','SOLICITADO','NAO SERA ATENDIDO','AGENDADO'])
listaAtendimento = SimpleVocabulary.fromValues(['Emprestimo de equipamento','Emprestimo de espaco','Equipe tecnica'])
sortTiposEvento = ['Aula','Defesa',u'Colacao','Formatura',u'Seminario',
'Palestra',u'Forum',u'Simposio','Mostra','Congresso','Encontro','Ensaio','Montagem',u'Manutencao',
u'Capacitacao','Workshop','Prova',u'Recepcao','Solenidade','Festividade',u'Reuniao']
sortTiposEvento.sort()
tiposEvento = SimpleVocabulary.fromValues(sortTiposEvento)
listaServicosExtras = SimpleVocabulary.fromValues(['Rede WiFi','Transmissao interna','Transmissao via internet','Traducao simultanea',])
listaVeiculos = SimpleVocabulary.fromValues(['Kombi','Caminhao','Carro'])

def telefoneValidation(data):
	tel = data.replace("(","")
	tel = tel.replace(")","")
	tel = tel.replace("-","")
	tel = tel.replace(" ","")
	if not tel.isdigit() or len(tel)<8 or data[-5]!= "-" or data[0]!="(" or data[3]!=")" or data.count(" ")>1:
	 	raise Invalid(_(u"O número deve ser no formato (XX)XXXXX-XXXX"))
	return True
	
	
def validateaddress(data):
    try:
        checkEmailAddress(data)
    except EmailAddressInvalid:
    	  raise Invalid(u"XXXX@XXX.XXX ")
    return True	
	
def validatetitle(data):
    if '"' in data or "'" in data:
       raise Invalid(u"Não é permitido aspas no nome do evento.")
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


permissaoAdm='sistema.agenda.modificaEvento'
class Ievento(form.Schema, IImageScaleTraversable):
    """
    Evento
    """
    form.write_permission(equipe=permissaoAdm)
    form.write_permission(categoria=permissaoAdm)             
    form.write_permission(atendimento=permissaoAdm)             

    title=schema.TextLine(title=u"Nome do evento",required=True,constraint=validatetitle)  
    id=schema.TextLine(title=u"Número identificador desta solicitação.")	    
    categoria=schema.Choice(title=u"Categoria",description=u'PARA O AGENDADOR: Informe se o evento é da UFMG (interno) ou não (externo)',required=False,vocabulary=listaDeCategorias)
    atendimento=schema.Set(title=u"Atendimento",description=u'PARA O AGENDADOR: Informe o tipo de atendimento que sera prestado.',required=False, value_type=schema.Choice(source=listaAtendimento))
    tipo=schema.Choice(title=u"Tipo",required=True,vocabulary=tiposEvento)	
    local=RelationList(title=u"Local",description=u'Escolha os espaços a serem agendados',required=True,value_type=RelationChoice(title=u'Local',required=True,source=pastaLocais))
    equipe=RelationList(title=u"Equipe",description=u'PARA O AGENDADOR: Informe a equipe para este evento',required=False,value_type=RelationChoice(title=u'Equipe',required=True,source=pastaEquipe))	
    previsaoDePublico=schema.TextLine(title=u"Previsão de Público",description=u'Informe a previsão do número de participantes',required=True,constraint=publicoValidation)
    servicosExtras=schema.Set(title=u"Serviços Extras",description=u'O evento necessita de algum destes serviços?',required=False, value_type=schema.Choice(source=listaServicosExtras))
    form.widget('servicosExtras', CheckBoxFieldWidget)
    form.widget('atendimento', CheckBoxFieldWidget)
	
    form.fieldset('dadosSolicitante',label=u"Dados do solicitante", fields=['responsavel','cpf','instituicao','unidade','telefone','celular','email'] ) 
    responsavel=schema.TextLine(title=u"Responsável pelo evento",description=u'Indique o nome completo do responsável pelo evento.',required=True)
    instituicao=schema.TextLine(title=u"Instituição",description=u'Informe qual a instituição ligada ao evento',required=True,default=u'UFMG')
    unidade=schema.TextLine(title=u"Unidade",description=u'Informe a unidade ou departamento que está fazendo a solicitação',required=True)
    telefone=schema.TextLine(title=u"Telefone",description=u'Informe o contato telefônico do responsável pelo evento',required=True,constraint=telefoneValidation,default=u'(31)3409-5000')
    celular=schema.TextLine(title=u"Celular",description=u'Informe o celular do responsável pelo evento',required=True,constraint=telefoneValidation)
    email=schema.TextLine(title=u"E-mail",description=u'Informe o email do responsável pelo evento',required=True,constraint=validateaddress)
    cpf=schema.TextLine(title=u"CPF",constraint=cpfValidation, description=u'Informe o cpf do responsável pelo evento',required=True)

    form.fieldset('detalhes',label=u"Detalhes do evento", fields=['description'] )
    form.widget('description', WysiwygFieldWidget)
    description=schema.Text(title=u"Descrição do evento",description=u"Informe os equipamentos, os serviços necessários e a programação do evento",required=True)		
    #anexo = NamedFile(title=u"Anexo",description=u"Quando requerido, adicione aqui o documento da unidade autorizando a realizacao de seu evento.", required=False)
    #programacao = NamedFile(title=u"Programacao",description=u"Quando possivel anexe a programacao completa do evento.", required=False)

    #ABA transporte	
    form.fieldset('transporte',label=u"Solicitacao de transporte", fields=[ 'setorTransporte','prioridadeTransporte','responsavelTransporte','emailTransporte','dataSaida',  	
    'dataRetorno',
    'tipoVeiculo',
    'numeroCarregadores',
    'materialTransportado',
    'dadosAdicionais',	
    'localOrigem',
    'localOrigemResponsavel',
    'localOrigemCelular',
    'localOrigemTelefoneFixo',
    'localOrigemMelhorHorario',
	'localOrigemSala',
    'localOrigemAndar',
    'localOrigemBloco',  	
    'localDestino',
    'localDestinoResponsavel',
    'localDestinoCelular',
    'localDestinoTelefoneFixo',
    'localDestinoMelhorHorario',
	'localDestinoSala',
    'localDestinoAndar',
    'localDestinoBloco',	
    'localDevolucao',
    'localDevolucaoResponsavel',
    'localDevolucaoCelular',
    'localDevolucaoTelefoneFixo',
    'localDevolucaoMelhorHorario',
	'localDevolucaoSala',
    'localDevolucaoAndar',
    'localDevolucaoBloco','estadoTransporte'] )	
    form.write_permission(dataSaida=permissaoAdm) 
    form.write_permission(dataRetorno=permissaoAdm)
    form.write_permission(tipoVeiculo=permissaoAdm)
    form.write_permission(numeroCarregadores=permissaoAdm)
    form.write_permission(materialTransportado=permissaoAdm)
    form.write_permission(dadosAdicionais=permissaoAdm)
	
    form.write_permission(localOrigem=permissaoAdm)
    form.write_permission(localOrigemResponsavel=permissaoAdm)
    form.write_permission(localOrigemCelular=permissaoAdm)
    form.write_permission(localOrigemTelefoneFixo=permissaoAdm)
    form.write_permission(localOrigemMelhorHorario=permissaoAdm)
    form.write_permission(localOrigemSala=permissaoAdm)
    form.write_permission(localOrigemAndar=permissaoAdm)
    form.write_permission(localOrigemBloco=permissaoAdm)  

	
    form.write_permission(localDestino=permissaoAdm)
    form.write_permission(localDestinoResponsavel=permissaoAdm)
    form.write_permission(localDestinoCelular=permissaoAdm)
    form.write_permission(localDestinoTelefoneFixo=permissaoAdm)
    form.write_permission(localDestinoMelhorHorario=permissaoAdm)
    form.write_permission(localDestinoSala=permissaoAdm)
    form.write_permission(localDestinoAndar=permissaoAdm)
    form.write_permission(localDestinoBloco=permissaoAdm)
	
    form.write_permission(localDevolucao=permissaoAdm)
    form.write_permission(localDevolucaoResponsavel=permissaoAdm)
    form.write_permission(localDevolucaoCelular=permissaoAdm)
    form.write_permission(localDevolucaoTelefoneFixo=permissaoAdm)
    form.write_permission(localDevolucaoMelhorHorario=permissaoAdm)
    form.write_permission(localDevolucaoSala=permissaoAdm)
    form.write_permission(localDevolucaoAndar=permissaoAdm)
    form.write_permission(localDevolucaoBloco=permissaoAdm)
    form.write_permission(setorTransporte=permissaoAdm)
    form.write_permission(emailTransporte=permissaoAdm)
    form.write_permission(responsavelTransporte=permissaoAdm)
	
	
    form.read_permission(responsavelTransporte=permissaoAdm) 		
    form.read_permission(emailTransporte=permissaoAdm) 	
    form.read_permission(dataSaida=permissaoAdm) 
    form.read_permission(dataRetorno=permissaoAdm)
    form.read_permission(tipoVeiculo=permissaoAdm)
    form.read_permission(numeroCarregadores=permissaoAdm)
    form.read_permission(materialTransportado=permissaoAdm)
    form.read_permission(dadosAdicionais=permissaoAdm)	
    form.read_permission(localOrigem=permissaoAdm)
    form.read_permission(localOrigemResponsavel=permissaoAdm)
    form.read_permission(localOrigemCelular=permissaoAdm)
    form.read_permission(localOrigemTelefoneFixo=permissaoAdm)
    form.read_permission(localOrigemMelhorHorario=permissaoAdm)
    form.read_permission(localOrigemSala=permissaoAdm)
    form.read_permission(localOrigemAndar=permissaoAdm)
    form.read_permission(localOrigemBloco=permissaoAdm)  	
    form.read_permission(localDestino=permissaoAdm)
    form.read_permission(localDestinoResponsavel=permissaoAdm)
    form.read_permission(localDestinoCelular=permissaoAdm)
    form.read_permission(localDestinoTelefoneFixo=permissaoAdm)
    form.read_permission(localDestinoMelhorHorario=permissaoAdm)
    form.read_permission(localDestinoSala=permissaoAdm)
    form.read_permission(localDestinoAndar=permissaoAdm)
    form.read_permission(localDestinoBloco=permissaoAdm)	
    form.read_permission(localDevolucao=permissaoAdm)
    form.read_permission(localDevolucaoResponsavel=permissaoAdm)
    form.read_permission(localDevolucaoCelular=permissaoAdm)
    form.read_permission(localDevolucaoTelefoneFixo=permissaoAdm)
    form.read_permission(localDevolucaoMelhorHorario=permissaoAdm)
    form.read_permission(localDevolucaoSala=permissaoAdm)
    form.read_permission(localDevolucaoAndar=permissaoAdm)
    form.read_permission(localDevolucaoBloco=permissaoAdm)
    form.read_permission(setorTransporte=permissaoAdm)
    form.read_permission(prioridadeTransporte=permissaoAdm)
    form.write_permission(prioridadeTransporte=permissaoAdm)
    
    setorTransporte=schema.TextLine(title=u"Setor responsavel pelo transporte",required=False)
    prioridadeTransporte=schema.Choice(title=u"Prioridade do transporte",source=listaPrioridadeTransporte,required=False)
    responsavelTransporte=schema.TextLine(title=u"Responsavel pelo transporte",required=False)
    emailTransporte=schema.TextLine(title=u"Email do responsavel pelo transporte",required=False,constraint=validateaddress)
    dataSaida = schema.Datetime(title=u'Data de saida',required=False)   	
    dataRetorno = schema.Datetime(title=u'Data de retorno',required=False)
    tipoVeiculo = schema.Choice(title=u"Tipo do Veiculo",source=listaVeiculos,required=False)
    numeroCarregadores=schema.TextLine(title=u"Numero de carregadores",constraint=publicoValidation,required=False)
    materialTransportado=schema.Text(title=u"Material Transportado",description=u"Informe os equipamentos que serao transportados nesta solicitacao.",required=False)		
    dadosAdicionais=schema.Text(title=u"Dados adicionais",description=u"Informe qualquer outra coisa relevante sobre o transporte.",required=False)		
	
    localOrigem=schema.TextLine(title=u"Unidade de Origem",required=False)
    localOrigemResponsavel=schema.TextLine(title=u"Responsavel no local de origem",required=False)
    localOrigemCelular=	schema.TextLine(title=u"Celular",constraint=telefoneValidation,default=u'(31)99999-9999',required=False)
    localOrigemTelefoneFixo=schema.TextLine(title=u"Telefone fixo",constraint=telefoneValidation,default=u'(31)3409-5000',required=False)	
    localOrigemMelhorHorario=schema.TextLine(title=u"Melhor horario para retirada",required=False)
    localOrigemSala=schema.TextLine(title=u"Sala de retirada",required=False)
    localOrigemAndar=schema.TextLine(title=u"Andar",required=False)
    localOrigemBloco=schema.TextLine(title=u"Bloco",required=False)    

	
    localDestino=schema.TextLine(title=u"Unidade de destino",required=False)
    localDestinoResponsavel=schema.TextLine(title=u"Responsavel no local de destino",required=False)
    localDestinoCelular=schema.TextLine(title=u"Celular",constraint=telefoneValidation,default=u'(31)99999-9999',required=False)
    localDestinoTelefoneFixo=schema.TextLine(title=u"Telefone fixo",constraint=telefoneValidation,default=u'(31)3409-5000',required=False)	
    localDestinoMelhorHorario=schema.TextLine(title=u"Melhor horario para recebimento",required=False)
    localDestinoSala=schema.TextLine(title=u"Sala de entrega",required=False)
    localDestinoAndar=schema.TextLine(title=u"Andar",required=False)
    localDestinoBloco=schema.TextLine(title=u"Bloco",required=False)
	
    localDevolucao=schema.TextLine(title=u"Unidade de devolucao",required=False)
    localDevolucaoResponsavel=schema.TextLine(title=u"Responsavel no local de devolucao",required=False)
    localDevolucaoCelular=schema.TextLine(title=u"Celular",constraint=telefoneValidation,default=u'(31)99999-9999',required=False)
    localDevolucaoTelefoneFixo=schema.TextLine(title=u"Telefone fixo",constraint=telefoneValidation,default=u'(31)3409-5000',required=False)	
    localDevolucaoMelhorHorario=schema.TextLine(title=u"Melhor horario para devolucao",required=False)
    localDevolucaoSala=schema.TextLine(title=u"Sala de entrega",required=False)
    localDevolucaoAndar=schema.TextLine(title=u"Andar",required=False)
    localDevolucaoBloco=schema.TextLine(title=u"Bloco",required=False)
	
	
    #ABA servicos gerais	
    form.fieldset('servicosGerais',label=u"Servicos gerais", fields=['setorServicosGerais',
	'responsavelServicosGerais',
	'emailServicosGerais' ,'estadoServicosGerais',
	'utilizarBanheiro',
	'responsavelutilizarBanheiro',
	'celularutilizarBanheiro',
	'fixoutilizarBanheiro','detalhesutilizarBanheiro',
	'ordemServicoPrevia',
	'detalhesordemServicoPrevia',
	'limpezaPrevia',
	'detalheslimpezaPrevia',
	'disponibilizaPaineis',
	'detalhesdisponibilizaPaineis',
	'disponibilizaSeguranca',
	'setordisponibilizaSeguranca','responsaveldisponibilizaSeguranca',
	'emaildisponibilizaSeguranca',
	'detalhesdisponibilizaSeguranca', 'estadoSeguranca',
	'disponibilizaEletrica','setordisponibilizaEletrica','responsaveldisponibilizaEletrica',
	'emaildisponibilizaEletrica','detalhesdisponibilizaEletrica','estadoEletrica'])	
	
    form.write_permission(setorServicosGerais=permissaoAdm)	
    form.read_permission(setorServicosGerais=permissaoAdm)	
    form.write_permission(utilizarBanheiro=permissaoAdm)	
    form.read_permission(utilizarBanheiro=permissaoAdm)	
    form.write_permission(responsavelutilizarBanheiro=permissaoAdm)	
    form.read_permission(responsavelutilizarBanheiro=permissaoAdm)
    form.write_permission(celularutilizarBanheiro=permissaoAdm)	
    form.read_permission(celularutilizarBanheiro=permissaoAdm)
    form.write_permission(fixoutilizarBanheiro=permissaoAdm)	
    form.read_permission(fixoutilizarBanheiro=permissaoAdm)
    form.write_permission(emailServicosGerais=permissaoAdm)	
    form.read_permission(emailServicosGerais=permissaoAdm)
    form.write_permission(responsavelServicosGerais=permissaoAdm)	
    form.read_permission(responsavelServicosGerais=permissaoAdm)
    setorServicosGerais=schema.TextLine(title=u"Setor responsavel pelos servicos gerais",required=False)
    responsavelServicosGerais=schema.TextLine(title=u"Responsavel pelos servicos gerais",required=False)
    emailServicosGerais=schema.TextLine(title=u"Email do responsavel pelos servicos gerais",required=False,constraint=validateaddress)
    utilizarBanheiro=schema.Choice(title=u"Necessita utilizar banheiro?",required=False,source=opcaoBanheiro)
    form.widget('utilizarBanheiro', RadioWidget,onclick=u'desabilitaCaixaTexto(this)')
    responsavelutilizarBanheiro=schema.TextLine(title=u"Responsavel pela guarda da chave",required=False)
    celularutilizarBanheiro=schema.TextLine(title=u"Celular",constraint=telefoneValidation,default=u'(31)99999-9999',required=False)
    fixoutilizarBanheiro=schema.TextLine(title=u"Telefone fixo",constraint=telefoneValidation,default=u'(31)3409-5000',required=False)	
    form.write_permission(detalhesutilizarBanheiro=permissaoAdm)	
    form.read_permission(detalhesutilizarBanheiro=permissaoAdm)	    
    detalhesutilizarBanheiro=schema.Text(title=u"Detalhes do uso dos banheiros",required=False)
	
    form.write_permission(ordemServicoPrevia=permissaoAdm)	
    form.read_permission(ordemServicoPrevia=permissaoAdm)
    ordemServicoPrevia=schema.Choice(title=u"Necessita ordem de servico previa?",required=False,source=opcaoServicoPrevio)
    form.widget('ordemServicoPrevia', RadioWidget,onclick=u'desabilitaCaixaTexto(this)')
    form.write_permission(detalhesordemServicoPrevia=permissaoAdm)	
    form.read_permission(detalhesordemServicoPrevia=permissaoAdm)	    
    detalhesordemServicoPrevia=schema.Text(title=u"Detalhes ordem servico previa",required=False)		
	
    form.write_permission(limpezaPrevia=permissaoAdm)	
    form.read_permission(limpezaPrevia=permissaoAdm)
    limpezaPrevia=schema.Choice(title=u"Necessita limpeza previa?",required=False,source=opcaoLimpeza)
    form.widget('limpezaPrevia', RadioWidget,onclick=u'desabilitaCaixaTexto(this)')
    form.write_permission(detalheslimpezaPrevia=permissaoAdm)	
    form.read_permission(detalheslimpezaPrevia=permissaoAdm)	    
    detalheslimpezaPrevia=schema.Text(title=u"Detalhes limpeza previa",required=False)
	
    form.write_permission(disponibilizaPaineis=permissaoAdm)	
    form.read_permission(disponibilizaPaineis=permissaoAdm)
    disponibilizaPaineis=schema.Choice(title=u"Necessita disponibilizar paineis expositores?",required=False,source=opcaoPaineis)
    form.widget('disponibilizaPaineis', RadioWidget,onclick=u'desabilitaCaixaTexto(this)')
    form.write_permission(detalhesdisponibilizaPaineis=permissaoAdm)	
    form.read_permission(detalhesdisponibilizaPaineis=permissaoAdm)	    
    detalhesdisponibilizaPaineis=schema.Text(title=u"Detalhes da disponibilizacao dos paineis",required=False)

    #ABA seguranca
    #form.fieldset('seguranca',label=u"Seguranca", fields=['setorSeguranca','disponibilizaSeguranca','detalhesdisponibilizaSeguranca', 'setorEletrica','disponibilizaEletrica'])	
    form.write_permission(disponibilizaSeguranca=permissaoAdm)		
    form.read_permission(disponibilizaSeguranca=permissaoAdm)
    form.write_permission(setordisponibilizaSeguranca=permissaoAdm)	
    form.read_permission(setordisponibilizaSeguranca=permissaoAdm)
    form.write_permission(emaildisponibilizaSeguranca=permissaoAdm)	
    form.read_permission(emaildisponibilizaSeguranca=permissaoAdm)
    form.write_permission(responsaveldisponibilizaSeguranca=permissaoAdm)	
    form.read_permission(responsaveldisponibilizaSeguranca=permissaoAdm)
    setordisponibilizaSeguranca=schema.TextLine(title=u"Setor responsavel pela seguranca",required=False)
    responsaveldisponibilizaSeguranca=schema.TextLine(title=u"Responsavel pela seguranca",required=False)
    emaildisponibilizaSeguranca=schema.TextLine(title=u"Email do responsavel pela seguranca",required=False,constraint=validateaddress)
    disponibilizaSeguranca=schema.Choice(title=u"Necessita seguranca local?",required=False,source=opcaoSeguranca)
    form.widget('disponibilizaSeguranca', RadioWidget,onclick=u'desabilitaCaixaTexto(this)')
    form.write_permission(detalhesdisponibilizaSeguranca=permissaoAdm)	
    form.read_permission(detalhesdisponibilizaSeguranca=permissaoAdm)	    
    detalhesdisponibilizaSeguranca=schema.Text(title=u"Detalhes da disponibilizacao de segurancas",required=False)
	
    #ABA apoio eletrica
    #form.fieldset('apoioEletrica',label=u"Apoio eletrica ", fields=['setorEletrica','disponibilizaEletrica' ])		
    form.write_permission(disponibilizaEletrica=permissaoAdm)	
    form.read_permission(disponibilizaEletrica=permissaoAdm)
    form.write_permission(setordisponibilizaEletrica=permissaoAdm)	
    form.read_permission(setordisponibilizaEletrica=permissaoAdm)
    form.write_permission(responsaveldisponibilizaEletrica=permissaoAdm)	
    form.read_permission(responsaveldisponibilizaEletrica=permissaoAdm)
    form.write_permission(emaildisponibilizaEletrica=permissaoAdm)	
    form.read_permission(emaildisponibilizaEletrica=permissaoAdm)	
    setordisponibilizaEletrica=schema.TextLine(title=u"Setor responsavel pela eletrica",required=False)	
    responsaveldisponibilizaEletrica=schema.TextLine(title=u"Responsavel pela eletrica",required=False)
    emaildisponibilizaEletrica=schema.TextLine(title=u"Email do responsavel pela eletrica",required=False,constraint=validateaddress)
    disponibilizaEletrica=schema.Choice(title=u"Necessita apoio da equipe de eletrica?",required=False,source=opcaoEletrica)
    form.widget('disponibilizaEletrica', RadioWidget,onclick=u'desabilitaCaixaTexto(this)')  
    form.write_permission(detalhesdisponibilizaEletrica=permissaoAdm)	
    form.read_permission(detalhesdisponibilizaEletrica=permissaoAdm)	
    detalhesdisponibilizaEletrica=schema.Text(title=u"Detalhes do apoio da equipe de eletrica",required=False)	
	
	
    form.write_permission(estadoTransporte=permissaoAdm)	
    form.read_permission(estadoTransporte=permissaoAdm)
    form.write_permission(estadoServicosGerais=permissaoAdm)	
    form.read_permission(estadoServicosGerais=permissaoAdm)
    form.write_permission(estadoSeguranca=permissaoAdm)	
    form.read_permission(estadoSeguranca=permissaoAdm)
    form.write_permission(estadoEletrica=permissaoAdm)	
    form.read_permission(estadoEletrica=permissaoAdm)
	
    estadoTransporte=schema.Choice(title=u"Estado do pedido de transporte",required=False,source=opcoesEstado)
    estadoServicosGerais=schema.Choice(title=u"Estado do pedido de servicos gerais",required=False,source=opcoesEstado)
    estadoSeguranca=schema.Choice(title=u"Estado do pedido de seguranca",required=False,source=opcoesEstado)	
    estadoEletrica=schema.Choice(title=u"Estado do pedido de eletrica",required=False,source=opcoesEstado)

    @invariant
    def validaDados(data):
      modificaEvento(data)
	  
	  

@form.default_value(field=Ievento['id'])
def idDefault(data):      
    return  random.getrandbits(64)
	
	
def substituiLetrasInvalidas(evento): 
	letras=[('ç','c'),('ã','a')]
	descricao = getattr(evento,'description')
	responsavel = getattr(evento,'responsavel')
	titulo = getattr(evento,'title')
	instituicao = getattr(evento,'instituicao')
	unidade = getattr(evento,'unidade')
	campos=[descricao,responsavel,titulo,instituicao,unidade]
	for campo in campos:
		for letra in letras:
			campo.replace(letra[0],letra[1])
	evento.unidade=unidade.replace(letra[0],letra[1])
	evento.instituicao=instituicao
	evento.title=titulo
	evento.responsavel=responsavel
	evento.description=descricao

	
@grok.subscribe(Ievento, IObjectAddedEvent)
def adicionaEvento(evento, event):  
  catalog = getUtility(ICatalog)
  intids = getUtility(IIntIds) 
  inicio=getattr(evento,'start')
  fim=getattr(evento,'end')
  haLocal=getattr(evento,'local')
  haEquipe=getattr(evento,'equipe')  
  titulosLocais=[]
  strLocalParaTitulo=''
  
  hoje=datetime.today()
  iniComp = datetime(year=inicio.astimezone(timezone(evento.timezone)).year,month=inicio.astimezone(timezone(evento.timezone)).month,day=inicio.astimezone(timezone(evento.timezone)).day,hour=inicio.astimezone(timezone(evento.timezone)).hour,minute=inicio.astimezone(timezone(evento.timezone)).minute)  
  if inicio and iniComp<hoje:
    msg="Data de inicio incorreta: "+str(iniComp.day)+"/"+str(iniComp.month)+"/"+str(iniComp.year)+" "+str(iniComp.hour)+":"+str(iniComp.minute)+". UTILIZE A TECLA BACKSPACE PARA VOLTAR E CORRRIGIR."
    evento.plone_utils.addPortalMessage(msg, 'error')
    raise Invalid(msg)
	
	
  if haLocal:
    if len(evento.local):   
        for local in evento.local:   
           i = getattr(local,'to_id',None)		
           if i:            
		    #source_object e o local
            source_object = intids.queryObject(i)
            titulo =  source_object.title
            titulosLocais.append(titulo)			
            if source_object.id!='externo':
             for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='local')):
              objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)
              wf = getToolByName(objEventoCadastrado,'portal_workflow')
              estado = wf.getInfoFor(objEventoCadastrado,'review_state')              		
              if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id and (estado=='agendado' or estado=='prereservado'):
                if (inicio >= objEventoCadastrado.start and inicio <= objEventoCadastrado.end) or (fim <= objEventoCadastrado.end and fim >= objEventoCadastrado.start) or (fim >= objEventoCadastrado.end and inicio <= objEventoCadastrado.start):
                  msg="LOCAL NAO DISPONIVEL:"+titulo+". Conflito de agendamento com uma solicitacao previamente aprovada. Solicitacao: "+objEventoCadastrado.title +". Codigo: "+objEventoCadastrado.id
                  evento.plone_utils.addPortalMessage(msg, 'error')				  				  
                  raise Invalid(msg)  
  else:
    if not haLocal or len(evento.local)==0:  
      evento.plone_utils.addPortalMessage('Selecione um ou mais locais para o evento. Pressione a tecla BACKSPACE para voltar.', 'error')				  				  
      raise Invalid('Local obrigatorio') 
	   
  for nomeLocal in titulosLocais:
    strLocalParaTitulo+=' '+nomeLocal
  evento.title = getattr(evento,'title') +' em ['+strLocalParaTitulo+']'
  if haEquipe:
    if len(evento.equipe):   
        for local in evento.equipe:    
          i = getattr(local,'to_id',None)		
          if i:            
            source_object = intids.queryObject(i)
            titulo =  source_object.title 	
            for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='equipe')):
              objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)
              wf = getToolByName(objEventoCadastrado,'portal_workflow')
              estado = wf.getInfoFor(objEventoCadastrado,'review_state')	 			  
              if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id and (estado=='agendado' or estado=='prereservado'):
                if (inicio >= objEventoCadastrado.start and inicio <= objEventoCadastrado.end) or (fim <= objEventoCadastrado.end and fim >= objEventoCadastrado.start) or (fim >= objEventoCadastrado.end and inicio <= objEventoCadastrado.start):
                  msg="EQUIPE NAO DISPONIVEL:"+titulo+". Conflito de agendamento com uma alocacao previamente aprovada. Solicitacao: "+objEventoCadastrado.title +". Codigo: "+objEventoCadastrado.id
                  evento.plone_utils.addPortalMessage(msg, 'error')
                  raise Invalid(msg)

  pai = aq_parent(aq_inner(evento))  
  if pai.id == 'agenda':
    clipboard = pai.manage_cutObjects([evento.id])
    dest = pai.get('preagenda')
    result = dest.manage_pasteObjects(clipboard)
    modified(result)
  enviaEmail(evento)
  

@grok.subscribe(Ievento, IObjectModifiedEvent)
def modificaEventoAposedicao(evento,event):  
  #if isinstance(event,IObjectModifiedEvent):
  intids = getUtility(IIntIds)       
  inicio=getattr(evento,'start',getattr(evento,'start',None))
  fim=getattr(evento,'end',getattr(evento,'end',None))
  haLocal=getattr(evento,'local')  
  titulosLocais=[]
  strLocalParaTitulo=''

  if haLocal:
    if len(haLocal):   
        for local in evento.local: 
           i = getattr(local,'to_id',None)		
           if i:            		    
            source_object = intids.queryObject(i)            
            titulo =  source_object.title 	
            titulosLocais.append(titulo)	
  else:
    if not haLocal or len(haLocal)==0:  
      evento.plone_utils.addPortalMessage('Selecione um ou mais locais para o evento.', 'error')				  				  
      #raise Invalid('Local obrigatorio') 
      raise WidgetActionExecutionError('local', Invalid('Selecione um ou mais locais para o evento.'))                  

			
  for nomeLocal in titulosLocais:
    strLocalParaTitulo+=' '+nomeLocal
  strtitle=getattr(evento,'title')
  i=strtitle.find('[')
  tituloAnterior=''
  if strtitle[i-4:i]==' em ':
    tituloAnterior = strtitle[:i-4]
  else:
    tituloAnterior = strtitle[:i]
  if i==-1:
    tituloAnterior = 'Evento de '+getattr(evento,'responsavel')
  evento.title = tituloAnterior +' em ['+strLocalParaTitulo+']'

#Executado ao adicionar o objeto a titulo de validacao com os dados anteriores a edicao
def modificaEvento(evento):    
  catalog = getUtility(ICatalog)
  intids = getUtility(IIntIds) 
  #inicio=getattr(evento,'start',getattr(evento.__context__,'start',None))
  #fim=getattr(evento,'end',getattr(evento.__context__,'end',None))
  inicio=getattr(evento,'start',None)
  fim=getattr(evento,'end',None)
  haLocal=getattr(evento,'local')
  haEquipe=getattr(evento,'equipe')   
  if haLocal and inicio and fim:
    if len(evento.local):   
        for local in evento.local:                          
            source_object = local
            titulo =  source_object.title 	            		
            if source_object.id!='externo':			
             for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='local')):
              objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)
              wf = getToolByName(objEventoCadastrado,'portal_workflow')
              estado = wf.getInfoFor(objEventoCadastrado,'review_state')	 
              if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id and (estado=='agendado' or estado=='prereservado'):
                if (inicio >= objEventoCadastrado.start and inicio <= objEventoCadastrado.end) or (fim <= objEventoCadastrado.end and fim >= objEventoCadastrado.start) or (fim >= objEventoCadastrado.end and inicio <= objEventoCadastrado.start):
                  msg="LOCAL NAO DISPONIVEL:"+titulo+". Conflito de agendamento com uma solicitacao previamente aprovada. Solicitacao: "+objEventoCadastrado.title +". Codigo: "+objEventoCadastrado.id                  
                  raise WidgetActionExecutionError('local', Invalid(msg))                  
                     
  if haEquipe and inicio and fim:
    if len(evento.equipe):   
        for local in evento.equipe:              
            source_object = local
            titulo =  source_object.title 	
            for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='equipe')):
              objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)
              wf = getToolByName(objEventoCadastrado,'portal_workflow')
              estado = wf.getInfoFor(objEventoCadastrado,'review_state')	 			  
              if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id and (estado=='agendado' or estado=='prereservado'):
                if (inicio >= objEventoCadastrado.start and inicio <= objEventoCadastrado.end) or (fim <= objEventoCadastrado.end and fim >= objEventoCadastrado.start) or (fim >= objEventoCadastrado.end and inicio <= objEventoCadastrado.start):
                  msg="EQUIPE NAO DISPONIVEL:"+titulo+". Conflito de agendamento com uma alocacao previamente aprovada. Solicitacao: "+objEventoCadastrado.title +". Codigo: "+objEventoCadastrado.id
                  raise WidgetActionExecutionError('equipe', Invalid(msg))
				  
  
@grok.subscribe(Ievento, IActionSucceededEvent)
def trasitaEvento(evento,event):  
      catalog = getUtility(ICatalog)
      intids = getUtility(IIntIds)        
      wf = getToolByName(evento,'portal_workflow')	  
      estadoLocal = wf.getInfoFor(evento,'review_state')
      if evento.local:
       if len(evento.local) and estadoLocal=='prereservado':   
         for loc in evento.local: 
           i = getattr(loc,'to_id',None)		
           if i:            
            source_object = intids.queryObject(i)
            titulo =  source_object.title        
            if source_object.id!='externo':			
             for eventoCadastrado in catalog.findRelations(dict(to_id=intids.getId(aq_inner(source_object)), from_attribute='local')):
              objEventoCadastrado = intids.queryObject(eventoCadastrado.from_id)              
              estado = wf.getInfoFor(objEventoCadastrado,'review_state')	 
              if objEventoCadastrado is not None and objEventoCadastrado.id != evento.id and (estado=='agendado' or estado=='prereservado'):
                if (evento.start >= objEventoCadastrado.start and evento.start <= objEventoCadastrado.end) or (evento.end <= objEventoCadastrado.end and evento.end >= objEventoCadastrado.start) or (evento.end >= objEventoCadastrado.end and evento.start <= objEventoCadastrado.start):				   
                  msg="LOCAL NAO DISPONIVEL:"+titulo+". Conflito de agendamento com uma solicitacao previamente aprovada. Solicitacao: "+objEventoCadastrado.title +". Codigo: "+objEventoCadastrado.id
                  evento.plone_utils.addPortalMessage(msg, 'error')
                  raise WorkflowException(Invalid(msg))				  
      enviaEmail(evento)
                  
def retiraAcento(entrada):	
	let = "çãàáéíóúâêõêâôü"
	substitutas={'ç':'c','ã':'a','à':'a','á':'a','é':'e','í':'i','ó':'o','ú':'u','â':'a','ê':'a','õ':'o','ê':'e','â':'a','ô':'o','ü':'u'}
	for acentuada in entrada:
		if substitutas.has_key(acentuada):
			entrada=entrada.replace(acentuada,substitutas[acentuada])
	return entrada

def enviaEmail(solicitacao):
	servidor = getToolByName(solicitacao,'MailHost')
	info = obtemTodasInformacoesDeConteudo(solicitacao)
	del info[solicitacao.id]['categoria']
	del info[solicitacao.id]['equipe']	
	mt = getToolByName(solicitacao,'portal_membership')
	emailAgendador = mt.getMemberById('agendador').email
	wf = getToolByName(solicitacao,'portal_workflow')
	estado = str(wf.getInfoFor(solicitacao,'review_state'))	
	comentarios = str(wf.getInfoFor(solicitacao,'comments'))
	#comentarios = str(comentarios.encode(
	resp=info[solicitacao.id]['responsavel']
	resp=retiraAcento(resp)
	titulo = retiraAcento(info[solicitacao.id]['title'])
	mensagem = "Solicitação de agendamento\n\n"
	mensagem = mensagem + 'EVENTO: '+ str(titulo.encode('iso-8859-1'))+'\n'
	mensagem = mensagem +"ESTADO ATUAL: "+str(estado).upper()+"\n\n"
	#mensagem = mensagem + str('responsavel').upper()+" "+ resp+"\n"    
	mensagem = mensagem + str('email:').upper()+" "+ str(info[solicitacao.id]['email'])+"\n"    
	mensagem = mensagem + str('cpf:').upper()+" "+ str(info[solicitacao.id]['cpf'])+"\n"    
	mensagem = mensagem + str('telefone:').upper()+" "+ str(info[solicitacao.id]['telefone'])+"\n\n"    
	
	strDia=str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).day)
	if solicitacao.start.astimezone(timezone(solicitacao.timezone)).day <10:
		strDia="0"+str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).day)
	
	strMes=str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).month)
	if solicitacao.start.astimezone(timezone(solicitacao.timezone)).month <10:
		strMes="0"+str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).month)
		
	strDiaf=str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).day)
	if solicitacao.end.astimezone(timezone(solicitacao.timezone)).day <10:
		strDiaf="0"+str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).day)
		
	strMesf=str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).month)
	if solicitacao.end.astimezone(timezone(solicitacao.timezone)).month <10:
		strMesf="0"+str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).month)
		
	strh=str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).hour)
	if solicitacao.start.astimezone(timezone(solicitacao.timezone)).hour <10:
		strh="0"+str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).hour)
		
	strm=str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).minute)
	if solicitacao.start.astimezone(timezone(solicitacao.timezone)).minute <10:
		strm="0"+str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).minute)
		
	strhf=str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).hour)
	if solicitacao.end.astimezone(timezone(solicitacao.timezone)).hour <10:
		strhf="0"+str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).hour)
		
	strmf=str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).minute)
	if solicitacao.end.astimezone(timezone(solicitacao.timezone)).minute <10:
		strmf="0"+str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).minute)
		
	dataInicial= strDia+'/'+strMes+' de '+str(solicitacao.start.astimezone(timezone(solicitacao.timezone)).year)
	dataFinal=strDiaf+'/'+strMesf+' de '+str(solicitacao.end.astimezone(timezone(solicitacao.timezone)).year)
	horaInicial=strh+':'+strm
	horaFinal=strhf+':'+strmf
	
	mensagem = mensagem + str("Data inicial: ").upper()+ dataInicial+' às '+horaInicial+"\n" 
	mensagem = mensagem + str("Data final: ").upper()+dataFinal+' até '+horaFinal+"\n\n" 
	mensagem = mensagem + str("Protocolo: ").upper()+str(info[solicitacao.id]['id'])+"\n\n" 
	mensagem = mensagem + str("OBS: ").upper()+str(comentarios)+"\n\n" 
	
	del info[solicitacao.id]['email']
	del info[solicitacao.id]['responsavel']
	del info[solicitacao.id]['local']
	del info[solicitacao.id]['cpf']
	del info[solicitacao.id]['id']
	del info[solicitacao.id]['telefone']	
	listaExclusao = ['open_end','sync_uid','whole_day','start','end','timezone','description','title','unidade','servicosextras']
	listaMaiusculo = ['DETALHESDISPONIBILIZASEGURANCA',
'PRIORIDADETRANSPORTE',
'DISPONIBILIZASEGURANCA',
'UTILIZARBANHEIRO',
'LOCALDEVOLUCAOMELHORHORARIO',
'ESTADOSERVICOSGERAIS',
'LOCALDESTINOSALA',
'CELULARUTILIZARBANHEIRO',
'EMAILDISPONIBILIZASEGURANCA',
'TIPOVEICULO',
'LOCALDEVOLUCAOBLOCO',
'LOCALORIGEMCELULAR',
'SERVICOSEXTRAS',
'LOCALORIGEMSALA',
'LOCALDESTINOCELULAR',
'CELULAR',
'DETALHESDISPONIBILIZAPAINEIS',
'LOCALDESTINOBLOCO',
'LOCALDEVOLUCAOANDAR',
'ORDEMSERVICOPREVIA',
'RESPONSAVELUTILIZARBANHEIRO',
'DADOSADICIONAIS',
'DATASAIDA',
'LOCALDEVOLUCAOSALA',
'LOCALDESTINOANDAR',
'DETALHESDISPONIBILIZAELETRICA',
'TIPO',
'DETALHESUTILIZARBANHEIRO',
'ESTADOELETRICA',
'SETORDISPONIBILIZAELETRICA',
'FIXOUTILIZARBANHEIRO',
'ESTADOSEGURANCA',
'MATERIALTRANSPORTADO',
'RESPONSAVELTRANSPORTE',
'LOCALORIGEMRESPONSAVEL',
'DETALHESORDEMSERVICOPREVIA',
'PREVISAODEPUBLICO',
'LOCALORIGEM',
'LOCALORIGEMBLOCO',
'RESPONSAVELSERVICOSGERAIS',
'EMAILDISPONIBILIZAELETRICA',
'LOCALORIGEMANDAR',
'LOCALDESTINORESPONSAVEL',
'LOCALDESTINOMELHORHORARIO',
'SETORSERVICOSGERAIS',
'RESPONSAVELDISPONIBILIZAELETRICA',
'EMAILTRANSPORTE',
'DISPONIBILIZAPAINEIS',
'RESPONSAVELDISPONIBILIZASEGURANCA',
'LIMPEZAPREVIA',
'LOCALORIGEMTELEFONEFIXO',
'DISPONIBILIZAELETRICA',
'SETORDISPONIBILIZASEGURANCA',
'ATENDIMENTO',
'NUMEROCARREGADORES',
'LOCALDESTINO',
'DETALHESLIMPEZAPREVIA',
'LOCALDEVOLUCAORESPONSAVEL',
'LOCALDEVOLUCAO',
'SETORTRANSPORTE',
'LOCALDESTINOTELEFONEFIXO',
'EMAILSERVICOSGERAIS',
'INSTITUICAO',
'LOCALDEVOLUCAOCELULAR',
'LOCALDEVOLUCAOTELEFONEFIXO',
'DATARETORNO',
'LOCALORIGEMMELHORHORARIO',
'ESTADOTRANSPORTE']
	for i in listaExclusao:
		if i in info[solicitacao.id].keys():
			del info[solicitacao.id][i]
	for M in info[solicitacao.id].keys():
		if M.upper() in listaMaiusculo:
			del info[solicitacao.id][M]
	lista=info[solicitacao.id].keys()
	for dado in lista:		
		mensagem = mensagem + str(dado).upper()+" "+ str(info[solicitacao.id][dado])+"\n"    
		
	mensagem = mensagem + "\n\n ESTES DADOS FORAM ENVIADOS APENAS PARA SEREM CONFERIDOS . ESTA MENSAGEM NUNCA DEVE SER RESPONDIDA."  
	emailsEnvolvidos = solicitacao.email#+";"+emailAgendador
	titulo="Proposta de agendamento de "+solicitacao.responsavel.encode('iso-8859-1')
	emailConta = 'nav@cac.ufmg.br'
	#existe um comando que é validateSingleEmailAddress para que serve?
	if servidor.smtp_host !='':
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
        valor=valor.decode('iso-8859-1')
      if isinstance(valor,list):
        valor=str(valor)          
      if isinstance(valor,set):
        valsaida=''	  
        for val in valor:
           valsaida=str(val)+' '
        valor=str(valsaida)          
        if valor== '':
          valor="nenhum"		
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


class SampleView(grok.View):
    """ sample view class """

    grok.context(Ievento)
    grok.require('sistema.agenda.visualizaEvento')


class Iemails(form.Schema):
	""" Define form fields """	
	   
	corpoEmailTransporte=schema.Text(title=u"Solicitacao de transporte",required=False)
	corpoEmailServicosGerais=schema.Text(title=u"Solicitacao de servicos gerais",required=False)
	corpoEmailSeguranca=schema.Text(title=u"Solicitacao de seguranca",required=False)
	corpoEmailEletrica=schema.Text(title=u"Solicitacao de apoio equipe eletrica",required=False)

@form.default_value(field=Iemails['corpoEmailTransporte'])
def corpoEmailTransporteDefaultValue(data):
	evento = data.context
	
	dSaida=getattr(evento,'dataSaida','')
	dRetorno=getattr(evento,'dataRetorno','')
	
	if dSaida==None:
		dSaida=''
		
	if dRetorno==None:
		dRetorno=''		
		
	if dSaida!='':
		
		strDia=str(dSaida.day)
		if dSaida.day <10:
			strDia="0"+str(dSaida.day)
		
		strMes=str(dSaida.month)
		if dSaida.month <10:
			strMes="0"+str(dSaida.month)
			
		strh=str(dSaida.hour)		
		if dSaida.hour <10:
			strh="0"+str(dSaida.hour)
		
		strm=str(dSaida.minute)
		if dSaida.minute <10:
			strm="0"+str(dSaida.minute)
	

			
	if dRetorno!='':
		
		strDiaf=str(dRetorno.day)
		if dRetorno.day <10:
			strDiaf="0"+str(dRetorno.day)
			
		strMesf=str(dRetorno.month)
		if dRetorno.month <10:
			strMesf="0"+str(dRetorno.month)
	
		strhf=str(dRetorno.hour)
		if dRetorno.hour <10:
			strhf="0"+str(dRetorno.hour)
			
		strmf=str(dRetorno.minute)
		if dRetorno.minute <10:
			strmf="0"+str(dRetorno.minute)
		
		dataInicial= strDia+'/'+strMes+' de '+str(dSaida.year)
		dataFinal=strDiaf+'/'+strMesf+' de '+str(dRetorno.year)
		horaInicial=strh+':'+strm
		horaFinal=strhf+':'+strmf
		dSaida=dataInicial+" "+horaInicial
		dRetorno=dataFinal+' '+horaFinal
	corpoEmail="""
Destinatario: %s
Copia: infra@cac.ufmg.br
Titulo do email: Solicitacao de transporte para %s (evento - %s)
=======
Prezados responsaveis do %s,

Atraves deste email, solicitamos o agendamento de transporte conforme indicado abaixo:

Prioridade deste pedido: %s  

Nome do evento: %s

Local de retirada: %s %s
Horario de retirada: %s 
Contato para retirada do material transportado: %s %s %s

Local de entrega: %s %s andar:%s bloco:%s
Horario de entrega: %s 
Contato para entrega do material transportado: %s %s %s

Apos o evento, retornar os itens transportados conforme:

Local de devolucao:%s %s
Horario de devolucao:%s
Contato para devolucao do material: %s %s %s

Para essa solicitacao, julgamos ser adequado o seguinte veiculo: %s
Com a seguinte equipe de apoio: %s carregadores

OBSERVACOES: %s . %s
""" %(evento.emailTransporte,dSaida,evento.prioridadeTransporte,evento.setorTransporte,evento.prioridadeTransporte,
evento.title,evento.localOrigem,evento.localOrigemSala,dSaida,
evento.localOrigemResponsavel,evento.localOrigemCelular,evento.localOrigemTelefoneFixo,
evento.localDestino,evento.localDestinoSala,evento.localDestinoAndar,evento.localDestinoBloco,evento.localDestinoMelhorHorario,
evento.localDestinoResponsavel,evento.localDestinoCelular,evento.localDestinoTelefoneFixo,
evento.localDevolucao,evento.localDevolucaoSala,dRetorno,
evento.localDevolucaoResponsavel,evento.localDevolucaoCelular,evento.localDevolucaoTelefoneFixo,
evento.tipoVeiculo,evento.numeroCarregadores,evento.materialTransportado,evento.dadosAdicionais)

	corpoEmail+="""
Duvidas, favor retornar este email para infra@cac.ufmg.br.

Obrigado,

Atenciosamente,

Infraestrutura CAC,
Tel : 3409-3861,
Predio da Biblioteca Central - 1 Andar.
Campus Pampulha
"""

	return corpoEmail.encode('iso-8859-1')

@form.default_value(field=Iemails['corpoEmailSeguranca'])
def corpoEmailSegurancaDefaultValue(data):
	evento = data.context
	strDia=str(evento.start.astimezone(timezone(evento.timezone)).day)
	if evento.start.astimezone(timezone(evento.timezone)).day <10:
		strDia="0"+str(evento.start.astimezone(timezone(evento.timezone)).day)
	
	strMes=str(evento.start.astimezone(timezone(evento.timezone)).month)
	if evento.start.astimezone(timezone(evento.timezone)).month <10:
		strMes="0"+str(evento.start.astimezone(timezone(evento.timezone)).month)
		
	strDiaf=str(evento.end.astimezone(timezone(evento.timezone)).day)
	if evento.end.astimezone(timezone(evento.timezone)).day <10:
		strDiaf="0"+str(evento.end.astimezone(timezone(evento.timezone)).day)
		
	strMesf=str(evento.end.astimezone(timezone(evento.timezone)).month)
	if evento.end.astimezone(timezone(evento.timezone)).month <10:
		strMesf="0"+str(evento.end.astimezone(timezone(evento.timezone)).month)
		
	strh=str(evento.start.astimezone(timezone(evento.timezone)).hour)
	if evento.start.astimezone(timezone(evento.timezone)).hour <10:
		strh="0"+str(evento.start.astimezone(timezone(evento.timezone)).hour)
		
	strm=str(evento.start.astimezone(timezone(evento.timezone)).minute)
	if evento.start.astimezone(timezone(evento.timezone)).minute <10:
		strm="0"+str(evento.start.astimezone(timezone(evento.timezone)).minute)
		
	strhf=str(evento.end.astimezone(timezone(evento.timezone)).hour)
	if evento.end.astimezone(timezone(evento.timezone)).hour <10:
		strhf="0"+str(evento.end.astimezone(timezone(evento.timezone)).hour)
		
	strmf=str(evento.end.astimezone(timezone(evento.timezone)).minute)
	if evento.end.astimezone(timezone(evento.timezone)).minute <10:
		strmf="0"+str(evento.end.astimezone(timezone(evento.timezone)).minute)
		
	dataInicial= strDia+'/'+strMes+' de '+str(evento.start.astimezone(timezone(evento.timezone)).year)
	dataFinal=strDiaf+'/'+strMesf+' de '+str(evento.end.astimezone(timezone(evento.timezone)).year)
	horaInicial=strh+':'+strm
	horaFinal=strhf+':'+strmf
	corpoEmail="""
Destinatario: %s
Copia: infra@cac.ufmg.br
Titulo do email: Solicitacao de Seguranca Universitaria para %s
=======
Prezado responsavel pela Seguranca Universitaria,

Atraves deste email, solicitamos apoio da seguranca universitaria conforme itens abaixo:

Nome do evento: %s
Data de comeco: %s
Data de Termino:%s
Contato: %s %s %s

Detalhes: %s

Duvidas favor retornar este email para infra@cac.ufmg.br.

Obrigado,

Atenciosamente,

Infraestrutura CAC,
Tel : 3409-3861,
Predio da Biblioteca Central - 1 Andar.
Campus Pampulha"""%(evento.emaildisponibilizaSeguranca,dataInicial+" "+horaInicial,
evento.title,dataInicial+" "+horaInicial,dataFinal+" "+horaFinal,evento.responsavel,evento.telefone,
evento.celular,evento.detalhesdisponibilizaSeguranca)
	return corpoEmail.encode('iso-8859-1')
	
@form.default_value(field=Iemails['corpoEmailServicosGerais'])
def corpoEmailServicosGeraisDefaultValue(data):
	evento = data.context
	strDia=str(evento.start.astimezone(timezone(evento.timezone)).day)
	if evento.start.astimezone(timezone(evento.timezone)).day <10:
		strDia="0"+str(evento.start.astimezone(timezone(evento.timezone)).day)
	
	strMes=str(evento.start.astimezone(timezone(evento.timezone)).month)
	if evento.start.astimezone(timezone(evento.timezone)).month <10:
		strMes="0"+str(evento.start.astimezone(timezone(evento.timezone)).month)
		
	strDiaf=str(evento.end.astimezone(timezone(evento.timezone)).day)
	if evento.end.astimezone(timezone(evento.timezone)).day <10:
		strDiaf="0"+str(evento.end.astimezone(timezone(evento.timezone)).day)
		
	strMesf=str(evento.end.astimezone(timezone(evento.timezone)).month)
	if evento.end.astimezone(timezone(evento.timezone)).month <10:
		strMesf="0"+str(evento.end.astimezone(timezone(evento.timezone)).month)
		
	strh=str(evento.start.astimezone(timezone(evento.timezone)).hour)
	if evento.start.astimezone(timezone(evento.timezone)).hour <10:
		strh="0"+str(evento.start.astimezone(timezone(evento.timezone)).hour)
		
	strm=str(evento.start.astimezone(timezone(evento.timezone)).minute)
	if evento.start.astimezone(timezone(evento.timezone)).minute <10:
		strm="0"+str(evento.start.astimezone(timezone(evento.timezone)).minute)
		
	strhf=str(evento.end.astimezone(timezone(evento.timezone)).hour)
	if evento.end.astimezone(timezone(evento.timezone)).hour <10:
		strhf="0"+str(evento.end.astimezone(timezone(evento.timezone)).hour)
		
	strmf=str(evento.end.astimezone(timezone(evento.timezone)).minute)
	if evento.end.astimezone(timezone(evento.timezone)).minute <10:
		strmf="0"+str(evento.end.astimezone(timezone(evento.timezone)).minute)
		
	dataInicial= strDia+'/'+strMes+' de '+str(evento.start.astimezone(timezone(evento.timezone)).year)
	dataFinal=strDiaf+'/'+strMesf+' de '+str(evento.end.astimezone(timezone(evento.timezone)).year)
	horaInicial=strh+':'+strm
	horaFinal=strhf+':'+strmf
	corpoEmail="""
Destinatario: %s
Copia: infra@cac.ufmg.br
Titulo do email: Solicitacao de servicos gerais para %s 
=======
Prezado responsavel pelos servicos gerais do %s,

Atraves deste email, solicitamos o agendamento de servicos gerais conforme indicado abaixo:

Nome do evento: %s
Data de comeco: %s
Data de Termino:%s
Contato: %s %s %s

""" %(evento.emailServicosGerais,dataInicial+" "+horaInicial,evento.setorServicosGerais,
evento.title,dataInicial+" "+horaInicial,dataFinal+" "+horaFinal,evento.responsavel,evento.telefone,
evento.celular)

	if evento.ordemServicoPrevia and evento.ordemServicoPrevia[0:3] != 'Nao':
		corpoEmail+="""
Solicitamos ordem de servico previa junto ao DEMAI para o evento: %s.
Detalhes:%s
"""%(evento.title, evento.detalhesordemServicoPrevia)

	if evento.limpezaPrevia and evento.limpezaPrevia[0:3] != 'Nao':
		corpoEmail+="""
Solicitamos a limpeza previa para: %s.
Detalhes:%s.
"""%(evento.title, evento.detalheslimpezaPrevia)

	if evento.utilizarBanheiro and evento.utilizarBanheiro[0:3] != 'Nao':
		corpoEmail+="""
Solicitamos a abertura dos banheiros para %s.
Detalhes: %s.
"""%(evento.title, evento.detalhesutilizarBanheiro)

	if evento.disponibilizaPaineis and evento.disponibilizaPaineis[0:3] != 'Nao':
		corpoEmail+="""
Solicitamos a disponibilidade de paineis expositores para o evento: %s.
Detalhes: %s.
"""%(evento.title, evento.detalhesdisponibilizaPaineis)

	corpoEmail+="""
Duvidas favor retornar este email para infra@cac.ufmg.br.

Obrigado,

Atenciosamente,

Infraestrutura CAC,
Tel : 3409-3861,
Predio da Biblioteca Central - 1 Andar.
Campus Pampulha
"""
	return corpoEmail.encode('iso-8859-1')


@form.default_value(field=Iemails['corpoEmailEletrica'])
def corpoEmailEletricaDefaultValue(data):
	evento = data.context
	strDia=str(evento.start.astimezone(timezone(evento.timezone)).day)
	if evento.start.astimezone(timezone(evento.timezone)).day <10:
		strDia="0"+str(evento.start.astimezone(timezone(evento.timezone)).day)
	
	strMes=str(evento.start.astimezone(timezone(evento.timezone)).month)
	if evento.start.astimezone(timezone(evento.timezone)).month <10:
		strMes="0"+str(evento.start.astimezone(timezone(evento.timezone)).month)
		
	strDiaf=str(evento.end.astimezone(timezone(evento.timezone)).day)
	if evento.end.astimezone(timezone(evento.timezone)).day <10:
		strDiaf="0"+str(evento.end.astimezone(timezone(evento.timezone)).day)
		
	strMesf=str(evento.end.astimezone(timezone(evento.timezone)).month)
	if evento.end.astimezone(timezone(evento.timezone)).month <10:
		strMesf="0"+str(evento.end.astimezone(timezone(evento.timezone)).month)
		
	strh=str(evento.start.astimezone(timezone(evento.timezone)).hour)
	if evento.start.astimezone(timezone(evento.timezone)).hour <10:
		strh="0"+str(evento.start.astimezone(timezone(evento.timezone)).hour)
		
	strm=str(evento.start.astimezone(timezone(evento.timezone)).minute)
	if evento.start.astimezone(timezone(evento.timezone)).minute <10:
		strm="0"+str(evento.start.astimezone(timezone(evento.timezone)).minute)
		
	strhf=str(evento.end.astimezone(timezone(evento.timezone)).hour)
	if evento.end.astimezone(timezone(evento.timezone)).hour <10:
		strhf="0"+str(evento.end.astimezone(timezone(evento.timezone)).hour)
		
	strmf=str(evento.end.astimezone(timezone(evento.timezone)).minute)
	if evento.end.astimezone(timezone(evento.timezone)).minute <10:
		strmf="0"+str(evento.end.astimezone(timezone(evento.timezone)).minute)
		
	dataInicial= strDia+'/'+strMes+' de '+str(evento.start.astimezone(timezone(evento.timezone)).year)
	dataFinal=strDiaf+'/'+strMesf+' de '+str(evento.end.astimezone(timezone(evento.timezone)).year)
	horaInicial=strh+':'+strm
	horaFinal=strhf+':'+strmf
	corpoEmail="""
Destinatario: %s
Copia: infra@cac.ufmg.br
Titulo do email: Solicitacao de apoio de equipe eletrica para %s
=======
Prezado responsavel pelo apoio de equipe eletrica,

Atraves deste email, solicitamos apoio da equipe de eletrica conforme itens abaixo:

Nome do evento: %s
Data de comeco: %s
Data de Termino:%s
Contato: %s %s %s

Detalhes:%s

Duvidas favor retornar este email para infra@cac.ufmg.br.

Obrigado,

Atenciosamente,

Infraestrutura CAC,
Tel : 3409-3861,
Predio da Biblioteca Central - 1 Andar.
Campus Pampulha"""%(evento.emaildisponibilizaEletrica,dataInicial+" "+horaInicial,
evento.title,dataInicial+" "+horaInicial,dataFinal+" "+horaFinal,evento.responsavel,evento.telefone,
evento.celular,evento.detalhesdisponibilizaEletrica)

	return corpoEmail.encode('iso-8859-1')
	
	
class emails(form.SchemaForm):
    """ Define Form handling
    """
    grok.name('emails')
    grok.require('sistema.agenda.modificaEvento')
    grok.context(Ievento)

    schema = Iemails
    ignoreContext = True

    label = u"Emails para solicitacao de recursos de atendimento"
    

