# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.security import checkPermission
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from z3c.relationfield.relation import RelationValue
from zope.intid.interfaces import IIntIds

from plone.dexterity.interfaces import IDexterityFTI
from zope.schema import getFieldsInOrder

from zope.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog
from Acquisition import aq_inner, aq_parent
from datetime import datetime,date,time
from pytz import timezone

class relatorio_geral_eventos(BrowserView):
	""" Render the title and description of item only (example)
	"""
	index = ViewPageTemplateFile("resources/relatorio_geral_eventos.pt")
	
	def render(self):
		return self.index()

	def __call__(self):
		return self.render()
	
	def obtemEstatisticasDeEventos(self):	
		dados={}
		TotalAgendados=0
		TotalEmSolicitacoes=0
		TotalTerminado=0
		TotalEmAnalise=0
		TotalCancelado=0
		TotalDeEventos=0		
		
		TotalDeCongressos=0
		TotalDeColacoes=0
		TotalDeAulas=0
		TotalOutros=0
		
		TotalCad1=0
		TotalCad2=0
		TotalReitoria=0
		TotalPraca=0
		TotalExterno=0
		
		DuracaoMedia=datetime.now()-datetime.now()
		
		dados['TotalAgendados']=0
		dados['TotalEmSolicitacoes']=0
		dados['TotalTerminado']=0
		dados['TotalEmAnalise']=0
		dados['TotalCancelado']=0
		dados['TotalDeEventos']=0		
		
		#dados['Congressos']=0
		#dados['Colacoes']=0
		#dados['Aulas']=0
		#dados['OutrosTiposDeEventos']=0
		
		#dados['Cad1']=0
		#dados['Cad2']=0
		#dados['Reitoria']=0
		#dados['Praca']=0
		#dados['Externo']=0
		
		#dados['DuracaoMedia']=datetime.now()-datetime.now()
		
		pastaAgenda = self.context     
		pastaSolicitacoes = self.context.preagenda
		
		wf = getToolByName(pastaAgenda,'portal_workflow')  
		intids = getUtility(IIntIds)		
		
		eventosSolicitados =pastaSolicitacoes.listFolderContents()
		eventosAgendados = pastaAgenda.listFolderContents()
					
		for evento in eventosSolicitados:
			if evento.portal_type =='sistema.agenda.evento':
				TotalDeEventos = TotalDeEventos+1
				estado = wf.getInfoFor(evento,'review_state')
				if estado=='solicitacao':
					TotalEmSolicitacoes=TotalEmSolicitacoes+1
				if estado=='agendado':
					TotalAgendados=TotalAgendados+1
				if estado=='em_analise':
					TotalEmAnalise=TotalEmAnalise+1
				if estado=='terminado':
					TotalTerminado=TotalTerminado+1
				if estado=='cancelado':
					TotalCancelado=TotalCancelado+1
				if evento.local:
				 if len(evento.local) and isinstance(evento.local[0], RelationValue):
					lista=evento.local					
					for local in lista:
						at=getattr(local,'to_id',None)
						if at and False:
							obj = intids.queryObject(at)
							if str(obj.unidade).upper()=='CAD1' or str(obj.unidade).upper()=='CAD 1':
								TotalCad1=TotalCad1+1
							if str(obj.unidade).upper()=='CAD2' or str(obj.unidade).upper()=='CAD 2':
								TotalCad2=TotalCad2+1
							if str(obj.unidade).upper()=='REITORIA':
								TotalReitoria=TotalReitoria+1
							if str(obj.unidade).upper()=='PRACA':
								TotalPraca=TotalPraca+1
							if str(obj.unidade).upper()=='EXTERNO':
								TotalExterno=TotalExterno+1								
			
				DuracaoMedia = DuracaoMedia + evento.end-evento.start			
				tipo = evento.tipo
				if tipo in ['Aula','Prova','Defesa']:
					TotalDeAulas=TotalDeAulas+1
				else:
					if tipo in ['Colacao','Formatura','Festividade']:
						TotalDeColacoes=TotalDeColacoes+1
					else:
						if tipo in ['Congresso','Simposio','Seminario','Palestra','Forum']:
							TotalDeCongressos=TotalDeCongressos+1
						else: 
							TotalOutros=TotalOutros+1
				
		for evento in eventosAgendados:
			if evento.portal_type =='sistema.agenda.evento':
				TotalDeEventos = TotalDeEventos+1
				estado = wf.getInfoFor(evento,'review_state')
				if estado=='solicitacao':
					TotalEmSolicitacoes=TotalEmSolicitacoes+1
				if estado=='agendado':
					TotalAgendados=TotalAgendados+1
				if estado=='em_analise':
					TotalEmAnalise=TotalEmAnalise+1
				if estado=='terminado':
					TotalTerminado=TotalTerminado+1
				if estado=='cancelado':
					TotalCancelado=TotalCancelado+1					
				if evento.local:
				  if len(evento.local) and isinstance(evento.local[0], RelationValue):
					lista=evento.local					
					for local in lista:
						at=getattr(local,'to_id',None)
						if at and False:
							obj = intids.queryObject(at)
							if str(obj.unidade).upper()=='CAD1' or str(obj.unidade).upper()=='CAD 1':
								TotalCad1=TotalCad1+1
							if str(obj.unidade).upper()=='CAD2' or str(obj.unidade).upper()=='CAD 2':
								TotalCad2=TotalCad2+1
							if str(obj.unidade).upper()=='REITORIA':
								TotalReitoria=TotalReitoria+1
							if str(obj.unidade).upper()=='PRACA':
								TotalPraca=TotalPraca+1
							if str(obj.unidade).upper()=='EXTERNO':
								TotalExterno=TotalExterno+1									
			
				DuracaoMedia = DuracaoMedia + evento.end-evento.start			
				tipo = evento.tipo
				if tipo in ['Aula','Prova','Defesa']:
					TotalDeAulas=TotalDeAulas+1
				else:
					if tipo in ['Colacao','Formatura','Festividade']:
						TotalDeColacoes=TotalDeColacoes+1
					else:
						if tipo in ['Congresso','Simposio','Seminario','Palestra','Forum']:
							TotalDeCongressos=TotalDeCongressos+1
						else: 
							TotalOutros=TotalOutros+1
		
		dados['TotalAgendados']=TotalAgendados
		dados['TotalEmSolicitacoes']=TotalEmSolicitacoes
		dados['TotalTerminado']=TotalTerminado
		dados['TotalCancelado']=TotalCancelado
		dados['TotalEmAnalise']=TotalEmAnalise
		dados['TotalDeEventos']=TotalDeEventos
		
		#dados['Congressos']= TotalDeCongressos
		#dados['Colacoes']=TotalDeColacoes
		#dados['Aulas']=TotalDeAulas
		#dados['OutrosTiposDeEventos']=TotalOutros
		
		#dados['Cad1']=TotalCad1
		#dados['Cad2']=TotalCad2
		#dados['Reitoria']=TotalReitoria
		#dados['Praca']=TotalPraca
		#dados['Externo']=TotalExterno		
		
		if TotalDeEventos:
			DuracaoMediaHoras = float(DuracaoMedia.seconds)/3600
			DuracaoMedia=round(DuracaoMediaHoras/TotalDeEventos,2)
		else:
			DuracaoMedia=0
		#dados['DuracaoMedia']=DuracaoMedia
		
		return dados
		
	def obtemTodasInformacoesDeConteudo(self,conteudo):
		intids = getUtility(IIntIds)
		tipo="sistema.agenda."+str(conteudo.Type())
		tipo=tipo.lower()
		schema = getUtility(IDexterityFTI, name=tipo).lookupSchema()
		campos=getFieldsInOrder(schema)    
		dados={}
		
		strDia=str(conteudo.start.astimezone(timezone(conteudo.timezone)).day)
		if conteudo.start.astimezone(timezone(conteudo.timezone)).day <10:
			strDia="0"+str(conteudo.start.astimezone(timezone(conteudo.timezone)).day)
		
		strMes=str(conteudo.start.astimezone(timezone(conteudo.timezone)).month)
		if conteudo.start.astimezone(timezone(conteudo.timezone)).month <10:
			strMes="0"+str(conteudo.start.astimezone(timezone(conteudo.timezone)).month)
			
		strDiaf=str(conteudo.end.astimezone(timezone(conteudo.timezone)).day)
		if conteudo.end.astimezone(timezone(conteudo.timezone)).day <10:
			strDiaf="0"+str(conteudo.end.astimezone(timezone(conteudo.timezone)).day)
			
		strMesf=str(conteudo.end.astimezone(timezone(conteudo.timezone)).month)
		if conteudo.end.astimezone(timezone(conteudo.timezone)).month <10:
			strMesf="0"+str(conteudo.end.astimezone(timezone(conteudo.timezone)).month)
			
		strh=str(conteudo.start.astimezone(timezone(conteudo.timezone)).hour)
		if conteudo.start.astimezone(timezone(conteudo.timezone)).hour <10:
			strh="0"+str(conteudo.start.astimezone(timezone(conteudo.timezone)).hour)
			
		strm=str(conteudo.start.astimezone(timezone(conteudo.timezone)).minute)
		if conteudo.start.astimezone(timezone(conteudo.timezone)).minute <10:
			strm="0"+str(conteudo.start.astimezone(timezone(conteudo.timezone)).minute)
			
		strhf=str(conteudo.end.astimezone(timezone(conteudo.timezone)).hour)
		if conteudo.end.astimezone(timezone(conteudo.timezone)).hour <10:
			strhf="0"+str(conteudo.end.astimezone(timezone(conteudo.timezone)).hour)
			
		strmf=str(conteudo.end.astimezone(timezone(conteudo.timezone)).minute)
		if conteudo.end.astimezone(timezone(conteudo.timezone)).minute <10:
			strmf="0"+str(conteudo.end.astimezone(timezone(conteudo.timezone)).minute)
			
		dados['dataInicial']= strDia+'/'+strMes+'/'+str(conteudo.start.year)
		dados['dataFinal']=strDiaf+'/'+strMesf+'/'+str(conteudo.end.year)
		dados['horaInicial']=strh+':'+strm
		dados['horaFinal']=strhf+':'+strmf
		
		for campo,val in campos:
			valor =getattr(conteudo,campo)
			idCampo = campo      
			valorStr=""
			if valor is None:
				valorStr=''
			else:     
				#se o campo for relacional      
				if isinstance(valor,list) and len(valor) and isinstance(valor[0], RelationValue):
						lista=valor						
						for educandoMatriculado in lista:
							at=getattr(educandoMatriculado,'to_id',None)
							if at:
								obj = intids.queryObject(at)
								valorStr+=str(obj.title.encode('iso-8859-1'))+" "
				else:
					valorStr=valor       							
				# se o campo for data
				if isinstance(valor,date):
					valorStr=str(valor)						
				if isinstance(valor,str):          
					valorStr=valor.decode('iso-8859-1')				
				if isinstance(valor,set):
					valorStr=[str(i) for i in valor]			
				if isinstance(valor,datetime):
					valorStr=str(valor)          
				if isinstance(valor,time):
					valorStr=str(valor)      
				if valor is callable:
					valorStr=valor()                    
				if isinstance(valor,bool):
					valorStr=str(valor)
				if isinstance(valor,NamedBlobImage) or isinstance(valor,NamedBlobFile):
					valorStr='arquivo anexado' 
			dados[idCampo]= valorStr        
		listaExclusao = ['open_end','sync_uid','whole_day','start','end','timezone','equipe','servicosExtras','cpf','categoria']
		for i in listaExclusao:
			if i in dados.keys():
				del dados[i]
		
		dados['Publico']=dados['previsaoDePublico']
		del dados['previsaoDePublico']
		del dados['description']
		return dados
	
	def obtemDadosDeEventos(self):	
		pastaAgenda = self.context     
		pastaSolicitacoes = self.context.preagenda
		result = []		  			 
		wf = getToolByName(pastaAgenda,'portal_workflow')     
		for evento in pastaSolicitacoes.listFolderContents():        
			if checkPermission('sistema.agenda.visualizaEvento', evento) and evento.portal_type=='sistema.agenda.evento':
				dados = self.obtemTodasInformacoesDeConteudo(evento)
				estado = wf.getInfoFor(evento,'review_state')	
				dados['estado']=estado                       
				result.append(dados)  
		for evento in pastaAgenda.listFolderContents():        
			if checkPermission('sistema.agenda.visualizaEvento', evento) and evento.portal_type=='sistema.agenda.evento':
				dados = self.obtemTodasInformacoesDeConteudo(evento)
				estado = wf.getInfoFor(evento,'review_state')
				dados['estado']=estado				
				result.append(dados)        
		return result
	 
