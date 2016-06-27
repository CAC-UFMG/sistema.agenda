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
from Products.CMFCore.interfaces import ISiteRoot
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget,CheckBoxFieldWidget

from plone.dexterity.interfaces import IDexterityFTI
from zope.schema import getFieldsInOrder

from zope.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog
from Acquisition import aq_inner, aq_parent

from Products.CMFPlone.utils import _createObjectByType
from five import grok
from plone.directives import form
from zope import schema
from z3c.form import button
from Products.statusmessages.interfaces import IStatusMessage

from datetime import datetime,time,date,timedelta
import time as time2
import random
import copy
import csv

diasSemana = ['Segunda','Terca','Quarta','Quinta','Sexta','Sabado','Domingo']
unidades=['EBA','ECI','EEFFTO','ENG','FACE','FAE','FAFICH','FALE','ICB','ICB-POS','ICEX','IGC','MUSICA','ODONTO','VET']

#Determina qual é o intervalo minimo de minutos das disciplinas
UNIDADE_DE_TEMPO=10
#Indica que a distribuição por unidade deve ser feita como um último passo sobre a solução
#Essa distribuição tem impacto direto na qualidade da solução

#Classe base para a disponibilidade de uma sala de aula
class Sala(object):
	capacidade=0
	horarioI = time()
	horarioF = time()	
	diaI=date(2000,1,1)
	diaF=date(2000,1,1)
	quadroDisponibilidade=None
	baseQuadroHorarios=None
	id=None
	
	
	def __init__(self,capacidade,horarioI,horarioF, diaI, diaF):
		self.capacidade = capacidade
		self.horarioI=horarioI
		self.horarioF=horarioF		
		self.diaI=diaI
		self.diaF=diaF	
		self.quadroDisponibilidade={}
		self.id = random.getrandbits(64)
		
		listaHorarios={}
		if self.baseQuadroHorarios==None:
			#cria uma lista de dias para esta solicitacao que chega atraves de um intervalo
			step = timedelta(days=1)
			start = self.diaI
			end = self.diaF
			diasDaSolicitacao=[]
			while start <= end:
				#Se o dia for um dos dias da solicitacao
				diasDaSolicitacao.append(start)			
				start += step
					
			#Acrescenta chaves de horario de 10 em 10 minutos
			for i in range(0,23):				
				min=0
				while min <= 50:
					listaHorarios[str(time(i,min))]=''
					min+=UNIDADE_DE_TEMPO								
		
		self.baseQuadroHorarios=listaHorarios
		
		for dia in diasDaSolicitacao:	
			chaveOcupacao = str(dia)		
			self.quadroDisponibilidade[chaveOcupacao]=copy.copy(self.baseQuadroHorarios)

	#varre o quadroDisponibilidade por dia da solicitacao buscando por algum id
	def disponivelPara(self,solicitacao):
		if self.capacidade<solicitacao.capacidade:
			return False
		for dia in solicitacao.diasDaSolicitacao:
			chaveOcupacao = str(dia)
			step = timedelta(minutes=UNIDADE_DE_TEMPO)
			start = datetime(2016,1,1,solicitacao.horarioI.hour,solicitacao.horarioI.minute)
			end = datetime(2016,1,1,solicitacao.horarioF.hour,solicitacao.horarioF.minute)			
			while start <= end:
				strHora = str(start.time())	
				if self.quadroDisponibilidade.has_key(chaveOcupacao):
					if self.quadroDisponibilidade[chaveOcupacao].has_key(strHora):
						if self.quadroDisponibilidade[chaveOcupacao][strHora] != '':
							return False
					else:
						return False
				else:
					return False
				start += step									
		return True
		
	#coloca o id da solicitacao na sala a cada 10 minutos entre horario inicial e final da solicitacao 
	def ocupa(self,solicitacao):		
		for dia in solicitacao.diasDaSolicitacao:
			chaveOcupacao = str(dia)			
			step = timedelta(minutes=UNIDADE_DE_TEMPO)
			start = datetime(2016,1,1,solicitacao.horarioI.hour,solicitacao.horarioI.minute)
			end = datetime(2016,1,1,solicitacao.horarioF.hour,solicitacao.horarioF.minute)
			while start <= end:
				strHora = str(start.time())	
				#Se a data solicitada esta dentro do atendimento da sala
				if self.quadroDisponibilidade.has_key(chaveOcupacao):
					self.quadroDisponibilidade[chaveOcupacao][strHora] = solicitacao.id
					solicitacao.atendida=True
				else:
					return False
				start += step	
		return True
				
	#retira o id da solicitacao de cada 10 minutos entre horario inicial e final da sala			
	def desocupaSolicitacao(self,solicitacao):					
		for dia in solicitacao.diasDaSolicitacao:
			chaveOcupacao = str(dia)
			step = timedelta(minutes=UNIDADE_DE_TEMPO)
			start = datetime(2016,1,1,solicitacao.horarioI.hour,solicitacao.horarioI.minute)
			end = datetime(2016,1,1,solicitacao.horarioF.hour,solicitacao.horarioF.minute)
			while start <= end:
				strHora = str(start.time())				
				if self.quadroDisponibilidade.has_key(chaveOcupacao):
					if self.quadroDisponibilidade[chaveOcupacao].has_key(strHora):
						if self.quadroDisponibilidade[chaveOcupacao][strHora]==solicitacao.id:
							self.quadroDisponibilidade[chaveOcupacao][strHora] = ''
							solicitacao.atendida=False
						else:
							return False
					else:
						return False
				else:
					return False
				start += step	
		return True
		
	def desocupa(self):				
		#Criar uma matriz para a lista de horarios e aprimorar este metodo
		for dia in self.quadroDisponibilidade.keys():	
			chaveOcupacao = dia		
			self.quadroDisponibilidade[chaveOcupacao]=copy.copy(self.baseQuadroHorarios)

			
#A classe solicitacao herda os dados de Sala e acrescenta infor
#coes da unidade e dias da semana da solicitacao
class Solicitacao(Sala):
	#acrescenta unidade a Solicitacao
	unidade=''
	#toda lista é compartilhada entre as instancias
	diaSemana=None
	diasDaSolicitacao=None
	quadroSolicitacao=None
	atendida=False
	ids=None
	disciplina=''
	curso=''
	cod=''
	turma=''
	professor=''
	contatoProfessor=''
	def __init__(self,capacidade,horarioI,horarioF,diaI, diaF,unidade,parDiaSemana,disciplina='',curso='',cod='',turma='',professor='',contatoProfessor=''):
		#construtor da classe mãe
		super(Solicitacao, self).__init__(capacidade,horarioI,horarioF, diaI, diaF)		
		#muito importante esse parâmetro aqui
		self.diaSemana=[]
		self.diasDaSolicitacao=[]
		self.atendida=False		
		self.disciplina=disciplina
		self.curso=curso
		self.cod=cod
		self.turma=turma
		self.professor=professor
		self.contatoProfessor=contatoProfessor
		
		if isinstance(parDiaSemana,list):
			self.diaSemana.extend(parDiaSemana)
		else:
			self.diaSemana.append(parDiaSemana)
		self.unidade = unidade
		
		#cria uma lista de dias para esta solicitacao que chega atraves de um intervalo
		for dia in self.quadroDisponibilidade.keys():	
			chaveOcupacao = dia		
			data=datetime.strptime(dia,'%Y-%m-%d').date()
			if not diasSemana[data.weekday()] in self.diaSemana:
				del self.quadroDisponibilidade[chaveOcupacao]
			else:
				self.diasDaSolicitacao.append(datetime.strptime(dia,'%Y-%m-%d').date())
		self.quadroSolicitacao=copy.copy(self.quadroDisponibilidade)
		self.quadroDisponibilidade=None
		
		if not Solicitacao.ids:
			Solicitacao.ids={}
			
		Solicitacao.ids[str(self.id)]=self
		
	#Avalia ao impacto ao se retirar a solicitacao da solucao
	def avaliaImpactoSemSolicitacao(self,agendamentos,solicitacoes,salas,objavaliacao):		
			
		haimpacto=False
		impacto =0
		ag=None
		#Passar a cada sala de agendamento verificando se ha a possibilidade de agendar 
		#para que seja visto qual o impacto deste agendamento
		for agendamento in agendamentos:
			if agendamento.solicitacao==self:
				ag=agendamento
				haimpacto=True
				break
				
		if haimpacto and ag!= None:
			nivel = objavaliacao.avalia()			
			#avalia a solicitacao quanto a numero de atendidos
			atendidos=0
			for solicitacao in solicitacoes:
				if solicitacao.atendida:
					atendidos+=1
			maxAtendidos=float(len(solicitacoes))
			avaliacaoAtendidos= float(atendidos-1)/maxAtendidos
			
			#avalia a solicitacao quanto a capacidade de atendidos
			capAtendidos=0
			totalSolicitado=0
			for solicitacao in solicitacoes:				
				if solicitacao.atendida:
					capAtendidos+=solicitacao.capacidade
				totalSolicitado+=solicitacao.capacidade
			
			avaliacaoCapAtendidos= float(capAtendidos-self.capacidade)/totalSolicitado
			
			minutosDesocupados=0
			horasTotais=0
			
			#avalia a solicitacao quanto a horas de atendidas
			for sala in salas:
				for chaveDia in sala.quadroDisponibilidade.keys():
					for chaveHorario in sala.quadroDisponibilidade[chaveDia].keys():
						horasTotais+=UNIDADE_DE_TEMPO
						if sala.quadroDisponibilidade[chaveDia][chaveHorario]!='':
							minutosDesocupados+=UNIDADE_DE_TEMPO
			
			
			for dia in self.diasDaSolicitacao:
				step = timedelta(minutes=UNIDADE_DE_TEMPO)
				start = datetime(2016,1,1,self.horarioI.hour,self.horarioI.minute)
				end = datetime(2016,1,1,self.horarioF.hour,self.horarioF.minute)
				while start <= end:					
					horasTotais+=UNIDADE_DE_TEMPO					
					start += step
					minutosDesocupados-=UNIDADE_DE_TEMPO									
			
			horasDesocupadas=float(minutosDesocupados)/60
			horasTotais = float(horasTotais)/60
			avaliacaoHoras = float(horasDesocupadas/horasTotais)
			
			#avalia a solicitacao na media das avaliacoes anteriores
			avaliacoes = [avaliacaoHoras,avaliacaoCapAtendidos,avaliacaoAtendidos]
			numMedidas = len(avaliacoes)
			
			medias = [(medida*100)/numMedidas for medida in avaliacoes]
			
			avaliacao=0
			
			for media in medias:
				avaliacao += media
				
			#retorna a diferenca entre o que ha na solucao e o que a solicitacao vai melhorar
			impacto =nivel-avaliacao		
		return impacto
		

		
	def obtemSolicitacaoPorId(self,id):
		return Solicitacao.ids[str(id)]
		
	#Verifica se as solicitacoes sao para um mesmo recurso
	def verificaIntersecaoHorarios(self,solicitacaoTeste):
		for dia in self.diasDaSolicitacao:
			if dia in solicitacaoTeste.diasDaSolicitacao:								
				start = datetime(2016,1,1,self.horarioI.hour,self.horarioI.minute)
				end = datetime(2016,1,1,self.horarioF.hour,self.horarioF.minute)
				startT = datetime(2016,1,1,self.horarioI.hour,self.horarioI.minute)
				endT = datetime(2016,1,1,self.horarioF.hour,self.horarioF.minute)
				if (start>=startT and start<=endT) or (end>=startT and end<=endT):
					return True						
		return False
	
	#Exibe uma matriz com os dias marcados para a solicitacao
	def exibe(self):
		out=""
		out2=""
		print "----------------Dias de semana da "+self.__class__.__name__+"---------------------"				
		for dia in diasSemana:
			numChar=len(dia)
			dif=10-numChar			
			out+=' '*(dif/2)+dia+' '*(dif/2)
			if dia in self.diaSemana:
				out2+="    X    "				
			else:
				out2+="         "
		print out
		print out2
		print "------------------------------------------------------------------"
		print "        Comecando em "+str(self.diaI.day)+"/"+str(self.diaI.month)+"/"+str(self.diaI.year)+" e terminando em "+str(self.diaF.day)+"/"+str(self.diaF.month)+"/"+str(self.diaF.year)
		print "==================================================================\n"

	#Exibe uma matriz com os dias marcados para a solicitacao
	def output(self):
		out=""
		out2=""
		saida=""
		saida+= "----------------Dias de semana da "+str(self.__class__.__name__)+"---------------------"				
		for dia in diasSemana:
			numChar=len(dia)
			dif=10-numChar			
			out+=' '*(dif/2)+dia+' '*(dif/2)
			if dia in self.diaSemana:
				out2+="    X    "				
			else:
				out2+="         "
		saida+= out
		saida+= out2
		saida+= "------------------------------------------------------------------"
		saida+= "        Comecando em "+str(self.diaI.day)+"/"+str(self.diaI.month)+"/"+str(self.diaI.year)+" e terminando em "+str(self.diaF.day)+"/"+str(self.diaF.month)+"/"+str(self.diaF.year)
		saida+= "==================================================================\n"
		return saida


#Agendamento de uma solucao
class Agendamento(object):
	sala=None
	solicitacao=None
	def __init__(self,sala,solicitacao):
		sala.ocupa(solicitacao)
		self.sala = sala
		self.solicitacao=solicitacao		
		
#Avaliacao de uma solucao
class Solucao(object):	
	avaliacaoFinal=None
	distribuicao={}
	def __init__(self):
		self.distribuicao={}		
		
	def exibeDistribuicao(self,solicitacoes):		
		print "Percentual de distribuicao"	
		self.atualizaContagemDistribuicao(solicitacoes)	
		print self.distribuicao
		
	def outputDistribuicao(self,solicitacoes):		
		saida=""
		saida+= "Percentual de distribuicao\n"	
		self.atualizaContagemDistribuicao(solicitacoes)
		for unidade in self.distribuicao.keys():
			saida+=str(unidade)+" "+str(self.distribuicao[unidade])+"%\n"		
		return saida
		
	def exibe(self,agendamentos,salas):
		print "-------------------Solucao de agendamentos---------------\n"
		print "---------------Indice:"+str(self.avaliacaoFinal)+"------------\n"
		for sala in salas:
			print ":::::::::::::::::: Sala:"+ str(sala.id)+" ::::::::::::::::::::::\n"
			dias = [dia for dia in sala.quadroDisponibilidade.keys()]
			dias.sort()
			exibidos={}
			diaExibido=''
			for dia in dias:	
				diaStr = dia.split('-')				
				print "::::::::::::::::::::::: Dia:"+diaStr[2]+"/"+diaStr[1]+"/"+diaStr[0]+" :::::::::::::::::::::::::::\n"
				horarios = [horario for horario in sala.quadroDisponibilidade[dia].keys() if sala.quadroDisponibilidade[dia][horario]!='']
				horarios.sort()					
				idSolicitacao=''
				if not len(horarios):
					print "                       -->DIA LIVRE<--\n"
				for horario in horarios:
					idSolicitacao=str(sala.quadroDisponibilidade[dia][horario])
					objS=agendamentos[0].solicitacao.obtemSolicitacaoPorId(idSolicitacao)				
				
					if not exibidos.has_key(idSolicitacao):
						exibidos[idSolicitacao]={}
						exibidos[idSolicitacao]['diasExibidos']=len(objS.diasDaSolicitacao)
						exibidos[idSolicitacao]['horarioExibido']=False
					
					#se nao foi exibido por horario
					if not exibidos[idSolicitacao]['horarioExibido']:
						print "=================================================================="
						print "                Id da solicitacao:"+idSolicitacao
						print "  	                        Unidade:"+objS.unidade
						print "Horario Inicial:"+str(objS.horarioI)+"                    Horario Final:"+str(objS.horarioF)+"\n"
						objS.exibe()							
						exibidos[idSolicitacao]['diasExibidos']-=1
						exibidos[idSolicitacao]['horarioExibido']=True
						diaExibido=dia
					#se ja foi exibido por horario
					else:
						if diaExibido!=dia:										
							print "=================================================================="
							print "                Id da solicitacao:"+idSolicitacao
							print "  	                        Unidade:"+objS.unidade
							print "Horario Inicial:"+str(objS.horarioI)+"                    Horario Final:"+str(objS.horarioF)+"\n"
							objS.exibe()								
							exibidos[idSolicitacao]['diasExibidos']-=1		
							diaExibido=dia												
						
		print "---------------------------------------------------------\n"
		print "-------------Indice:"+str(self.avaliacaoFinal)+"------------\n"
	
	
	def output(self,agendamentos,salas):
		out=""
		out+= "-------------------Solucao de agendamentos---------------\n"
		out+= "---------------Indice:"+str(self.avaliacaoFinal)+"------------\n"
		for sala in salas:
			out+= ":::::::::::::::::: Sala:"+ str(sala.id)+" ::::::::::::::::::::::\n"
			dias = [dia for dia in sala.quadroDisponibilidade.keys()]
			dias.sort()
			exibidos={}
			diaExibido=''
			for dia in dias:	
				diaStr = dia.split('-')				
				out+= "::::::::::::::::::::::: Dia:"+diaStr[2]+"/"+diaStr[1]+"/"+diaStr[0]+" :::::::::::::::::::::::::::\n"
				horarios = [horario for horario in sala.quadroDisponibilidade[dia].keys() if sala.quadroDisponibilidade[dia][horario]!='']
				horarios.sort()					
				idSolicitacao=''
				if not len(horarios):
					out+= "                       -->DIA LIVRE<--\n"
				for horario in horarios:
					idSolicitacao=str(sala.quadroDisponibilidade[dia][horario])
					objS=agendamentos[0].solicitacao.obtemSolicitacaoPorId(idSolicitacao)				
				
					if not exibidos.has_key(idSolicitacao):
						exibidos[idSolicitacao]={}
						exibidos[idSolicitacao]['diasExibidos']=len(objS.diasDaSolicitacao)
						exibidos[idSolicitacao]['horarioExibido']=False
					
					#se nao foi exibido por horario
					if not exibidos[idSolicitacao]['horarioExibido']:
						out+= "=================================================================="
						out+= "                Id da solicitacao:"+idSolicitacao
						out+= "  	                        Unidade:"+objS.unidade
						out+= "Horario Inicial:"+str(objS.horarioI)+"                    Horario Final:"+str(objS.horarioF)+"\n"
						out+=objS.output()							
						exibidos[idSolicitacao]['diasExibidos']-=1
						exibidos[idSolicitacao]['horarioExibido']=True
						diaExibido=dia
					#se ja foi exibido por horario
					else:
						if diaExibido!=dia:										
							out+= "=================================================================="
							out+= "                Id da solicitacao:"+idSolicitacao
							out+= "  	                        Unidade:"+objS.unidade
							out+= "Horario Inicial:"+str(objS.horarioI)+"                    Horario Final:"+str(objS.horarioF)+"\n"
							out+=objS.output()								
							exibidos[idSolicitacao]['diasExibidos']-=1		
							diaExibido=dia												
						
		out+= "---------------------------------------------------------\n"
		out+= "-------------Indice:"+str(self.avaliacaoFinal)+"------------\n"
		return out
	
	def outputCSV(self,agendamentos,salas):
		out=""
		out+="disciplina;unidade;alunos;sala.id;diaSemana;curso;cod;turma;professor;diaI;diaF;contatoProfessor"+"\n"
		for agendamento in agendamentos:
			solicitacao=agendamento.solicitacao
			sala = agendamento.sala												
			if solicitacao.atendida:			
				out+=str(solicitacao.disciplina)+";"+str(solicitacao.unidade)+";"+str(solicitacao.capacidade)+";"+str(sala.id)+";"+str(solicitacao.diaSemana)+";"+str(solicitacao.curso)+";"+str(solicitacao.cod)+";"+str(solicitacao.turma)+";"+str(solicitacao.professor)+";"+str(solicitacao.diaI)+";"+str(solicitacao.diaF)+";"+str(solicitacao.contatoProfessor)+"\n"
		return out
		
	def otimizaOcupacaoHorario(self,solicitacao,sala,solucaoAtual):
		#Uma ocupacao de maior duracao é melhor que varias ocupacoes pequenas que nao tomam todo o tempo		
		d=datetime(2016,1,1,solicitacao.horarioF.hour,solicitacao.horarioF.minute)
		tempoDeOcupacaoDaSolicitacao = (d-timedelta(hours=solicitacao.horarioI.hour))-timedelta(minutes=solicitacao.horarioI.minute)
		tempoDeOcupacaoDaSolicitacao=tempoDeOcupacaoDaSolicitacao.time()
		for dia in solicitacao.diasDaSolicitacao:
			idsTrocados=[]
			idsSolicitacoesTroca={}
			tempoOcupado=0
			chaveOcupacao = str(dia)
			step = timedelta(minutes=UNIDADE_DE_TEMPO)
			start = datetime(2016,1,1,solicitacao.horarioI.hour,solicitacao.horarioI.minute)
			end = datetime(2016,1,1,solicitacao.horarioF.hour,solicitacao.horarioF.minute)
			while start <= end:
				strHora = str(start.time())				
				if sala.quadroDisponibilidade.has_key(chaveOcupacao):
					if sala.quadroDisponibilidade[chaveOcupacao].has_key(strHora):
						if sala.quadroDisponibilidade[chaveOcupacao][strHora]!='':
							tempoOcupado+=UNIDADE_DE_TEMPO
							if not idsSolicitacoesTroca.has_key(str(solicitacao.id)):
								idsSolicitacoesTroca[str(solicitacao.id)]=[]										
							if not sala.quadroDisponibilidade[chaveOcupacao][strHora] in idsSolicitacoesTroca[str(solicitacao.id)]:
								idsSolicitacoesTroca[str(solicitacao.id)].append(sala.quadroDisponibilidade[chaveOcupacao][strHora])
					#else:
					#	continue
				#else:
				#	continue
				start += step	
			
			horasOcupadas =tempoOcupado/60
			minutosOcupados=((float(tempoOcupado)/60)-horasOcupadas)*60
			tempoDeOcupacaoDaSalaNoHorarioDaSolicitacao=time(horasOcupadas,int(minutosOcupados))	
						
			if [horasOcupadas,minutosOcupados]!=[0,0] and tempoDeOcupacaoDaSalaNoHorarioDaSolicitacao<tempoDeOcupacaoDaSolicitacao:
				#Caso uma troca seja feita havera impacto no indice pois varios eventos serao retirados para
				# para a entrada de um evento de maior duracao, entao a diversidade diminui, mas o tempo de 
				#ocupacao aumenta
							
				if not solicitacao.id in idsTrocados:
					for solicitacaoMenor in idsSolicitacoesTroca[str(solicitacao.id)]:
						objSolicitacaoMenor=solicitacao.obtemSolicitacaoPorId(solicitacaoMenor)					
						sala.desocupaSolicitacao(objSolicitacaoMenor)														
						#print "Trocou "+str(solicitacao.id)+" por "+str(solicitacaoMenor)
							
					if sala.disponivelPara(solicitacao):
						novoAgendamento=Agendamento(sala,solicitacao)
						solucaoAtual.append(novoAgendamento)	
						idsTrocados.append(solicitacao.id)
									
					#Uma vez que asolicitacao foi agendada deveria-se ir para uma outra solicitacao
					return 1
		return 0
	
	def otimizaOcupacaoCapacidade(self,solicitacoes,solucaoAtual):
		#Verifica dentre as solicitacoes nao atendidas se a
		#capacidade das atendidas é menor e se é possivel trocar
		print "Otimizando ocupacao por capacidade"
		for solicitacao in solicitacoes:
			if not solicitacao.atendida:
				for agendamento in solucaoAtual:			
					capSolicitada=solicitacao.capacidade
					capAtendido=agendamento.solicitacao.capacidade
					if capAtendido<capSolicitada:
						solicitacaoAntiga = agendamento.solicitacao
						agendamento.sala.desocupaSolicitacao(agendamento.solicitacao)
						if agendamento.sala.disponivelPara(solicitacao):
							agendamento.sala.ocupa(solicitacao)							
						else:
							agendamento.sala.ocupa(solicitacaoAntiga)
						
	def otimizaOcupacaoDistribuicaoUnidades(self,solicitacoes,solucaoAtual,nivelDistribuicao,salas,objavaliacao):
		#Verifica dentre as solicitacoes nao atendidas se as
		#capacidade das atendidas é menor e se é possivel trocar
		print "Otimizando entre Unidades"
		self.atualizaContagemDistribuicao(solicitacoes)				
		iteracoes=0		
		niveisReceber=[]
		niveisCeder=[]
		for nivel in self.distribuicao.keys():
			if nivelDistribuicao.has_key(nivel):
				#Se o nivel do usuario for maior que o da solucao atual
				#entao a unidade tem que receber mais agendamentos
				nivelusuario=nivelDistribuicao[nivel]
				nivelSolucao=self.distribuicao[nivel]
				if nivelSolucao<nivelusuario:
					niveisReceber.append(nivel)					
				else: 
					niveisCeder.append(nivel)	
					
		self.removeRestantes(solucaoAtual,solicitacoes,niveisCeder,nivelDistribuicao,salas,objavaliacao)
		self.adicionaRestantes(solucaoAtual,solicitacoes,niveisReceber,nivelDistribuicao,salas,objavaliacao)
		
		self.atualizaContagemDistribuicao(solicitacoes)							
		niveisReceber=[]
		niveisCeder=[]
		for nivel in self.distribuicao.keys():
			if nivelDistribuicao.has_key(nivel):
				#Se o nivel do usuario for maior que o da solucao atual
				#entao a unidade tem que receber mais agendamentos
				nivelusuario=nivelDistribuicao[nivel]
				nivelSolucao=self.distribuicao[nivel]
				if nivelSolucao<nivelusuario:
					niveisReceber.append(nivel)					
				if nivelSolucao>nivelusuario: 
					niveisCeder.append(nivel)
		#passa entre os niveis de cada unidade na solucao atual			
		#obtem as unidades que têm agendamentos sobrando troca entre as duas
		print "Realizando troca entre unidades"
		for nivelReceber in niveisReceber:
			for nivelCeder in niveisCeder:
				unidades=[nivelReceber,nivelCeder]
				
				numMaxReceber=len([j for j in self.obtemSolicitacoesDaUnidade(solicitacoes,nivelReceber) if not j.atendida])
				numMaxCeder=len([i for i in self.obtemSolicitacoesDaUnidade(solicitacoes,nivelCeder) if i.atendida])
				
				iteracaoMaxima=min(numMaxReceber,numMaxCeder)				
				continua=True
				iteracoes=0
				while continua and iteracoes <= iteracaoMaxima:					
					continua=self.otimizaEntreUnidades(solucaoAtual,solicitacoes,unidades,salas)
					iteracoes+=1							
	
	def removeRestantes(self,solucaoAtual,solicitacoes,unidadesCeder,distribuicaoAlvo,salas,objavaliacao):
		print "Retirando remanescentes"				
		for unidadeCeder in unidadesCeder:
			indiceAlvo = distribuicaoAlvo[unidadeCeder]
			indiceAtual = self.distribuicao[unidadeCeder]			
			j=0
			numMaxCeder=len([i for i in self.obtemSolicitacoesDaUnidade(solicitacoes,unidadeCeder) if i.atendida])			
			while indiceAtual >= indiceAlvo and j<numMaxCeder:
				self.removeSolicitacaoDaUnidade(unidadeCeder,solucaoAtual,objavaliacao,solicitacoes,salas)
				self.atualizaContagemDistribuicao(solicitacoes)	
				indiceAtual = self.distribuicao[unidadeCeder]				
				j+=1
				#print "Removeu com indice:"+str(indiceAtual)+" Ideal:"+str(indiceAlvo)
		
		
	def adicionaRestantes(self,solucaoAtual,solicitacoes,unidadesCeder,distribuicaoAlvo,salas,objavaliacao):
		print "Adicionando remanescentes"				
		for unidadeCeder in unidadesCeder:
			indiceAlvo = distribuicaoAlvo[unidadeCeder]
			indiceAtual = self.distribuicao[unidadeCeder]	
			j=0			
			numMaxCeder=len([i for i in self.obtemSolicitacoesDaUnidade(solicitacoes,unidadeCeder) if not i.atendida])						
			while indiceAtual <= indiceAlvo and j<numMaxCeder:				
				self.adicionaSolicitacaoDaUnidade(unidadeCeder,solucaoAtual,objavaliacao,solicitacoes,salas)
				self.atualizaContagemDistribuicao(solicitacoes)	
				indiceAtual = self.distribuicao[unidadeCeder]	
				j=j+1				
		return
	
	def removeSolicitacaoDaUnidade(self,unidade,agendamentos,objavaliacao,solicitacoes,salas):		
		sala=None
		sol=None
		ag=None
		for agendamento in agendamentos:			
			if agendamento.solicitacao.unidade==unidade and agendamento.solicitacao.atendida:
					sala=agendamento.sala
					sol=agendamento.solicitacao
					ag=agendamento
					sala.desocupaSolicitacao(sol)
					agendamentos.remove(ag)	
					break
					#print "Realizou otimizacao de unidades removendo"
					
	def adicionaSolicitacaoDaUnidade(self,unidade,agendamentos,objavaliacao,solicitacoes,salas):				
		ag=None
		continua = True
		for solicitacao in solicitacoes:
			if solicitacao.unidade==unidade and not solicitacao.atendida:
				i=len(salas)-1				
				while i>=0 and continua:
					sala=salas[i]
					if sala.disponivelPara(solicitacao) and not solicitacao.atendida:																		
						ag=Agendamento(sala,solicitacao)									
						agendamentos.append(ag)	
						continua=False
					i-=1
				if not continua:
					break
						
	
	def obtemSolicitacoesDaUnidade(self,solicitacoes,unidade):
		resultado=[]
		for solicitacao in solicitacoes:
			if solicitacao.unidade==unidade:
				resultado.append(solicitacao)
		return resultado

	def otimizaEntreUnidades(self,solucaoAtual,solicitacoes,unidades,salas):
		#Desagendar a pior solicitacao de unidades[1] e agendar a melhor de unidades[0]						
		solicitacaoMelhorEntrar=None
		lstsolicitacaoMelhorCeder=[]						
		listaTravadas=[]	
		saida=False	
		#Obtem as solicitacoes da unidade a receber que nao foram atendidas
		for solicitacao in self.obtemSolicitacoesDaUnidade(solicitacoes,unidades[0]):
			if not solicitacao.atendida:
				outras = self.obtemSolicitacoesDaUnidade(solicitacoes,unidades[1])
				listaTravadas = [i for i in outras if solicitacao.verificaIntersecaoHorarios(i)]
				solicitacaoMelhorEntrar = solicitacao								
					
			#Obtem as solicitacoes da unidade a ceder que já foram atendidas			
			if solicitacaoMelhorEntrar:			
				for solicitacao in listaTravadas:
					if solicitacao.unidade ==unidades[1]:					
						lstsolicitacaoMelhorCeder.append(solicitacao)									 
		
				# Remove a solicitacao da unidade a ceder da solucao, caso nao haja eh um sinal para parar			
				lstSalasCeder=[]
				for solicitacaoMelhorCeder in lstsolicitacaoMelhorCeder:
					if solicitacaoMelhorEntrar and solicitacaoMelhorCeder != solicitacaoMelhorEntrar:					
						for agendamento in solucaoAtual:			
							if agendamento.solicitacao==solicitacaoMelhorCeder:
								agendamento.sala.desocupaSolicitacao(solicitacaoMelhorCeder)
								solucaoAtual.remove(agendamento)										
								lstSalasCeder.append(agendamento.sala)
								saida=True
	
				#Adiciona a solicitacao da unidade a receber, caso nao haja eh um sinal para parar		
				for sala in lstSalasCeder:			
					if sala.disponivelPara(solicitacaoMelhorEntrar):
						novoAg = Agendamento(sala,solicitacaoMelhorEntrar)
						solucaoAtual.append(novoAg)	
						self.atualizaContagemDistribuicao(solicitacoes)					
						saida=True
		#quando nao tiver solicitacoes para trocar ira retornar falso
		return saida
		
	def buscaSolucaoAlternativa(self,solucaoAtual,salas,solicitacoes,nivelDistribuicao,objavaliacao):				
		print "Buscando solucao Alternativa"
		for solicitacao in solicitacoes:
			if not solicitacao.atendida:
				#sera necessário desagendar algo para que ela caiba pois
				#essas solicitacoes ja passaram por todas as salas				
				for sala in salas:
					resultado=self.otimizaOcupacaoHorario(solicitacao, sala,solucaoAtual)									
					#Se a troca foi realizada passa para a proxima solicitacao nao atendida
					if resultado:								
						break				
		print "Otimizou ocupacao por horario"						
		resultado=self.otimizaOcupacaoCapacidade(solicitacoes, solucaoAtual)								

		if len(solucaoAtual):
			return solucaoAtual
		else:
			return None		

	def liberaTodasReservas(self,agendamentos):		
		for agendamento in agendamentos:
			#sempre que desocupa for chamado, as solicitacoes tem que ser liberadas apos
			agendamento.sala.desocupa()
			agendamento.solicitacao.atendida=False
			agendamentos.remove(agendamento)
			
	def atualizaContagemDistribuicao(self,solicitacoes):					
		self.distribuicao={}
		totalPorUnidade={}
		percentualDistribuicao={}
		for solicitacao in solicitacoes:						
			if not self.distribuicao.has_key(solicitacao.unidade):
				self.distribuicao[solicitacao.unidade]=0
			if solicitacao.atendida:
				self.distribuicao[solicitacao.unidade]+=1	
			if not totalPorUnidade.has_key(solicitacao.unidade):
				totalPorUnidade[solicitacao.unidade]=0
			totalPorUnidade[solicitacao.unidade]+=1
				
		for unidade in self.distribuicao.keys():
			self.distribuicao[unidade] = float(self.distribuicao[unidade])/totalPorUnidade[unidade]			
		
		
			
					
	#Dispoe na ordem de chegada as solicitacoes nas salas
	def solucaoInicial(self,solicitacoes,salas):
		solucaoInicial = []
		print "Criando solucao inicial"
		
		for solicitacao in solicitacoes:
			for sala in salas:
				if sala.disponivelPara(solicitacao):
					novoAgendamento=Agendamento(sala,solicitacao)
					solucaoInicial.append(novoAgendamento)					
					break
				else:
					continue				
		if len(solucaoInicial):
			return solucaoInicial
		else:
			return None
	
	#Método central que dá a solucao do problema
	def resolve(self,solucaoAtual,solicitacoes,salas,nivelAceitavel, nivelDistribuicao,pOTIMIZAR_ENTRE_UNIDADES):		
		
		if not solucaoAtual:
			solucaoAtual = self.solucaoInicial(solicitacoes,salas)			

		avaliacao = Avaliacao(solucaoAtual,solicitacoes,salas)
		resultado=avaliacao.avalia()
		if resultado >= nivelAceitavel[0] and resultado <= nivelAceitavel[1]:
			self.avaliacaoFinal=resultado	
			if pOTIMIZAR_ENTRE_UNIDADES:
				self.otimizaOcupacaoDistribuicaoUnidades(solicitacoes, solucaoAtual,nivelDistribuicao,salas,avaliacao)									
			return solucaoAtual			
		else:					
			solucaoAlternativa = self.buscaSolucaoAlternativa(solucaoAtual,salas,solicitacoes,nivelDistribuicao,avaliacao)
			if solucaoAlternativa:			
				nivelRestrito=[int(resultado),nivelAceitavel[1]]
				print "Reduzindo um nivel para:"+str(nivelRestrito)+". Nivel anterior: "+str(resultado)+"\n"
				return self.resolve(solucaoAlternativa,solicitacoes,salas,nivelRestrito,nivelDistribuicao,False)
			else:
				return None
				
#Avaliacao de uma solucao
class Avaliacao(object):
	solucao=None
	solicitacoes=None
	salas=None
	def __init__(self,solucao,solicitacoes, salas):		
		self.solucao = solucao	
		self.solicitacoes = solicitacoes
		self.salas=salas
	
	def avaliaAtendidos(self,solicitacoes):
		#ver quantas solicitacoes ficaram de fora
		atendidos=0
		for solicitacao in solicitacoes:
			if solicitacao.atendida:
				atendidos+=1
		maxAtendidos=float(len(solicitacoes))
		avaliacaoAtendidos= float(atendidos)/maxAtendidos
		return avaliacaoAtendidos
		
	def avaliaCapacidadeAtendidos(self,solicitacoes):
		#ver número de atendidos nas solicitacoes 
		capAtendidos=0
		totalSolicitado=0
		for solicitacao in solicitacoes:
			if solicitacao.atendida:
				capAtendidos+=solicitacao.capacidade
			totalSolicitado+=solicitacao.capacidade
			
		
		avaliacaoCapAtendidos= float(capAtendidos)/totalSolicitado
		return avaliacaoCapAtendidos
	
		
	def avaliaOcupacaoHoras(self,salas):
		#ver quanto de horario de sala ficou sem agendamento
		minutosDesocupados=0
		horasTotais=0
		for sala in salas:
			for chaveDia in sala.quadroDisponibilidade.keys():
				for chaveHorario in sala.quadroDisponibilidade[chaveDia].keys():
					horasTotais+=UNIDADE_DE_TEMPO
					if sala.quadroDisponibilidade[chaveDia][chaveHorario]!='':
						minutosDesocupados+=UNIDADE_DE_TEMPO
							
		horasDesocupadas=float(minutosDesocupados)/60
		horasTotais = float(horasTotais)/60
		avaliacaoHoras = float(horasDesocupadas/horasTotais)
		return avaliacaoHoras
			
	#Funcao Fitness, faz avaliacao de criterios e entrega a media
	def avalia(self):
	
		if self.solucao:
			avaliacaoAtendidos = self.avaliaAtendidos(self.solicitacoes)	
			
			avaliacaoHoras = self.avaliaOcupacaoHoras(self.salas)		
			
			avaliaCapacidadeAtendidos = self.avaliaCapacidadeAtendidos(self.solicitacoes)
			
			avaliacoes=[avaliacaoAtendidos,avaliacaoHoras,avaliaCapacidadeAtendidos]
			
			numMedidas = len(avaliacoes)
			
			medias = [(medida*100)/numMedidas for medida in avaliacoes]
			
			avaliacao=0
			
			for media in medias:
				avaliacao += media
						
			return avaliacao
		else:
			return None




class Iagendamento_de_salas(form.Schema):
	""" Define form fields """
	
	csv_solicitacoes = NamedFile(title=u"Arquivo CSV das SOLICITACOES")
	csv_salas = NamedFile(title=u"Arquivo CSV das SALAS")
	form.widget("distribuir", SingleCheckBoxFieldWidget)
	distribuir=schema.Bool(title=u"Distribuir entre unidades?",required=True,default=True)
	indiceSolucao=schema.TextLine(title=u"Indice alvo para a solucao",description=u"Insira um número entre 0 e 100", required=True,default=u"64")
	dataI = schema.Date(title=u'Data inicial de atendimento')   
	dataF = schema.Date(title=u'Data final de atendimento')   
	restricoes=schema.Text(title=u"Percentual de atendimento por unidade", description=u"Preencha no formato abaixo com números entre 0.0 e 1.0",required=True,default=u"EBA:0.99\nECI:0.98\nENG:1\nICB:0.96\nICEX:1\nEEFFTO:1\nFACE:1\nFAE:0.95\nFAFICH:0.95\nFALE:0.98\nICB-POS:1\nIGC:1\nMUSICA:1\nODONTO:1\nVET:1")
							
@form.default_value(field=Iagendamento_de_salas['dataI'])
def dataIDefaultValue(data):
	anoAtual= datetime.today().year
	return datetime(anoAtual,2,1)

@form.default_value(field=Iagendamento_de_salas['dataF'])
def dataFDefaultValue(data):
	anoAtual= datetime.today().year	
	return datetime(anoAtual,12,23)
	 
class agendamento_de_salas(form.SchemaForm):
    """ Define Form handling
    """
    grok.name('agendamentoDeSalas')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = Iagendamento_de_salas
    ignoreContext = True

    label = u"Agendamento de salas"
    description = u"Sistema para criação de matriz de horarios de aulas"

    def leSolicitacoes(self,arquivo):		
		solicitacoes=[]
		
		conjlinhas=arquivo.splitlines()		
		for linha in conjlinhas:              
				registros = linha.split(';')     
				unidade = registros[1]
				disciplina = registros[2]
				codDisciplina = registros[3]
				turma = registros[4]
				capacidade = int(registros[5])
				
				diaDaSemana = registros[6]
				
				horarioInicio = datetime.strptime(registros[7], '%H:%M')
				horarioFim = datetime.strptime(registros[8], '%H:%M')
				
				dataInicio = datetime.strptime(registros[9], '%Y/%m/%d')
				dataFim = datetime.strptime(registros[10], '%Y/%m/%d')			
				
				solicitacaoAtual = Solicitacao(capacidade,horarioInicio.time(),horarioFim.time(),dataInicio.date(),dataFim.date(),unidade,diaDaSemana,disciplina,'',codDisciplina,turma)
				solicitacoes.append(solicitacaoAtual)      
		return solicitacoes
		
    def leSalas(self,arquivo,horarioInicioAtendimento,horarioFimAtendimento,diaInicioAtendimento,diaFimAtendimento):		
		salas=[]
		
		linhas=arquivo.splitlines()		
		for linha in linhas:              
				registros= linha.split(';')				
				capacidade = int(registros[0])
			
				salaAtual = Sala(capacidade,horarioInicioAtendimento,horarioFimAtendimento,diaInicioAtendimento,diaFimAtendimento)
				salas.append(salaAtual)      
		return salas
		
    @button.buttonAndHandler(u'Enviar')
    def handleApply(self, action):
		data, errors = self.extractData()        

		if errors:
			self.status = self.formErrorsMessage
			return

		#Configuracoes basicas de horario
		horarioInicioAtendimento = time(7,0)
		horarioFimAtendimento = time(23,00)

		#Configuracoes basicas de dia
		diaInicioAtendimento = date(data["dataI"].year,data["dataI"].month,data["dataI"].day)
		diaFimAtendimento = date(data["dataF"].year,data["dataF"].month,data["dataF"].day)
		
		#Configuracoes basicas do total de salas e solicitacoes
		
		#lista de salas e solicitacoes 
		salas=[]
		solicitacoes=[]
			
		raiz =self.context
				
		solicitacoes=self.leSolicitacoes(data["csv_solicitacoes"].data)  
		salas=self.leSalas(data["csv_salas"].data,horarioInicioAtendimento,horarioFimAtendimento,diaInicioAtendimento,diaFimAtendimento)  				
		
		solucao = Solucao()

		#Nivel de avaliacao da solucao baseado na otimizacao de horario
		#otimizacao de capacidade
		#otimizacao de numero de atendimento
		nivelAceitavel=[data["indiceSolucao"],100]
		
		OTIMIZAR_ENTRE_UNIDADES=data["distribuir"]
		strDistro=data["restricoes"]
		
		strDistro=strDistro.splitlines()
		niveisDistribuicao={}
		for k in strDistro:
			chave=str(k.split(':')[0])
			valor=float(k.split(':')[1])
			niveisDistribuicao[chave]=float(valor)
		
		info=""
		info+= 'Horario de inicio : '+str(datetime.now().hour)+':'+str(datetime.now().minute)+"\n"
		ini=time2.time()
		agendamentosFinais=solucao.resolve(None,solicitacoes,salas,nivelAceitavel,niveisDistribuicao,OTIMIZAR_ENTRE_UNIDADES)
		fim=time2.time()
		#lista com as solicitacoes que nao foram agendadas
		naoAgendadas = [sol for sol in solicitacoes if sol.atendida==False]
		solAgendadas = [sol for sol in solicitacoes if sol.atendida]

		#exibe a matriz de agendamento por sala por dia
		#solucao.exibe(agendamentosFinais,salas)
		
		info+= "---------------------------------------------\n"
		info+= "Numero total de solicitacoes: "+ str(len(solicitacoes))+"\n"
		info+= "Solicitacoes agendadas: "+ str(len(solAgendadas))+"\n"
		info+= "Solicitacoes nao agendadas: " +str(len(naoAgendadas))+"\n"
		info+= "Percentual de atendimento: " +str(float(len(solAgendadas)*100)/len(solicitacoes))+" %\n"
		info+= "Indice de avaliacao da solucao:"+ str(solucao.avaliacaoFinal)+"\n"
		info+= "Tempo gasto:"+ str((fim-ini)/60)+" minutos\n"
		info+= "---------------------------------------------\n"
		info+= solucao.outputDistribuicao(solicitacoes)		
		saida = solucao.outputCSV(agendamentosFinais,salas)
		sdm = self.context.session_data_manager
		session = sdm.getSessionData(create=True)
		session.set("info", info)
		session.set("saida", saida)
		
		IStatusMessage(self.request).addStatusMessage(u"Solucao encontrada para o melhor agendamento das solicitacoes!","info")

		contextURL = raiz.absolute_url()
		self.request.response.redirect(contextURL+"/@@download_agendamento_salas")
		
    
    @button.buttonAndHandler(u"Cancelar")
    def handleCancel(self, action):
		contextURL = self.context.absolute_url()
		self.request.response.redirect(contextURL)