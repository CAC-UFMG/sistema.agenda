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
		TotalDeEventos=0
		
		TotalDeCongressos=0
		TotalDeColacoes=0
		TotalDeAulas=0
		TotalOutros=0
		
		TotalCad1=0
		TotalCad2=0
		
		DuracaoMedia=datetime.now()-datetime.now()
		
		dados['TotalAgendados']=0
		dados['TotalEmSolicitacoes']=0
		dados['TotalTerminado']=0
		dados['TotalEmAnalise']=0
		dados['TotalDeEventos']=0
		
		dados['Congressos']=0
		dados['Colacoes']=0
		dados['Aulas']=0
		dados['Outros']=0
		
		dados['Cad1']=0
		dados['Cad2']=0
		
		dados['DuracaoMedia']=datetime.now()-datetime.now()
		
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
				if evento.local:
				 if len(evento.local) and isinstance(evento.local[0], RelationValue):
					lista=evento.local					
					for local in lista:
						at=getattr(local,'to_id',None)
						if at:
							obj = intids.queryObject(at)
							if str(obj.unidade).upper()=='CAD1' or str(obj.unidade).upper()=='CAD 1':
								TotalCad1=TotalCad1+1
							if str(obj.unidade).upper()=='CAD2' or str(obj.unidade).upper()=='CAD 2':
								TotalCad2=TotalCad2+1
			
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
				if len(evento.local) and isinstance(evento.local[0], RelationValue):
					lista=evento.local					
					for local in lista:
						at=getattr(local,'to_id',None)
						if at:
							obj = intids.queryObject(at)
							if str(obj.unidade).upper()=='CAD1' or str(obj.unidade).upper()=='CAD 1':
								TotalCad1=TotalCad1+1
							if str(obj.unidade).upper()=='CAD2' or str(obj.unidade).upper()=='CAD 2':
								TotalCad2=TotalCad2+1
			
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
		dados['TotalEmAnalise']=TotalEmAnalise
		dados['TotalDeEventos']=TotalDeEventos
		
		dados['Congressos']=TotalDeCongressos
		dados['Colacoes']=TotalDeColacoes
		dados['Aulas']=TotalDeAulas
		dados['Outros']=TotalOutros
		
		dados['Cad1']=TotalCad1
		dados['Cad2']=TotalCad2
		
		if TotalDeEventos:
			DuracaoMediaHoras = float(DuracaoMedia.seconds)/3600
			DuracaoMedia=round(DuracaoMediaHoras/TotalDeEventos,2)
		else:
			DuracaoMedia=0
		dados['DuracaoMedia']=DuracaoMedia
		
		return dados
		
	def obtemTodasInformacoesDeConteudo(self,conteudo):
		intids = getUtility(IIntIds)
		tipo="sistema.agenda."+str(conteudo.Type())
		tipo=tipo.lower()
		schema = getUtility(IDexterityFTI, name=tipo).lookupSchema()
		campos=getFieldsInOrder(schema)    
		dados={}
		dados['dataInicial']= str(conteudo.start.day)+'/'+str(conteudo.start.month)+' de '+str(conteudo.start.year)
		dados['dataFinal']=str(conteudo.end.day)+'/'+str(conteudo.end.month)+' de '+str(conteudo.end.year)
		dados['horaInicial']=str(conteudo.start.hour)+':'+str(conteudo.start.minute)
		dados['horaFinal']=str(conteudo.end.hour)+':'+str(conteudo.end.minute)
		for campo,val in campos:
			valor =getattr(conteudo,campo)
			idCampo = campo      
			if valor is None:
				valor=''
			else:     
				#se o campo for relacional      
				if isinstance(valor,list) and len(valor) and isinstance(valor[0], RelationValue):
						lista=valor
						valor=[]
						for educandoMatriculado in lista:
							at=getattr(educandoMatriculado,'to_id',None)
							if at:
								obj = intids.queryObject(at)
								valor.append(obj.title)
				else:
					valor=str(valor)          							
				# se o campo for data
				if isinstance(valor,date):
					valor=str(valor)						
				if isinstance(valor,str):          
					valor=valor.decode('utf-8')				
				if isinstance(valor,set):
					valor=[str(i) for i in valor]
				if isinstance(valor,datetime):
					valor=str(valor)          
				if isinstance(valor,time):
					valor=str(valor)      
				if valor is callable:
					valor=valor()                    
				if isinstance(valor,bool):
					valor=str(valor)
				if isinstance(valor,NamedBlobImage) or isinstance(valor,NamedBlobFile):
					valor='arquivo anexado' 
			dados[idCampo]= valor        
		del dados['sync_uid']
		del dados['whole_day']
		del dados['timezone']
		del dados['open_end']
		del dados['equipe']
		del dados['servicosExtras']
		del dados['cpf']
		del dados['start']
		del dados['end']
		del dados['categoria']
		dados['Publico']=dados['previsaoDePublico']
		del dados['previsaoDePublico']
		return dados
	
	def obtemDadosDeEventos(self):	
		pastaAgenda = self.context     
		pastaSolicitacoes = self.context.preagenda
		result = []
		hoje=datetime.today()   
		vazio=True	 
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
	 