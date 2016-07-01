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

permissaoAdm='sistema.agenda.modificaRecurso'
class Iagendamento(form.Schema, IImageScaleTraversable):
	"""
	Agendamentos de aulas
	"""
	
	title = schema.TextLine(title=_(u"Titulo deste conjunto de agendamentos"))
	id=schema.TextLine(title=u"Numero identificador")	
	
	info=schema.Text(title=u"Informacoes do processo")
	saida=schema.Text(title=u"Planilha CSV",description=u"Copie e cole este texto em um arquivo e salve como .CSV")

@form.default_value(field=Iagendamento['saida'])
def saidaDefaultValue(data):
	sdm = data.context.session_data_manager
	session = sdm.getSessionData(create=True)
	solucao=""
	if session.has_key('saida'):	
		solucao= str(session['saida']) or "Sem processamento."
		del session['saida']
	return solucao
	
@form.default_value(field=Iagendamento['info'])
def infoDefaultValue(data):
	sdm = data.context.session_data_manager
	session = sdm.getSessionData(create=True)
	solucao=""
	if session.has_key('info'):
		solucao= str(session['info']) or "Sem processamento."
		del session['info']
	return solucao
	 	

@form.default_value(field=Iagendamento['id'])
def idDefault(data):      
    return  random.getrandbits(64)
	
class agendamento(Item):
    grok.implements(Iagendamento)

    # Add your class methods and properties here
    pass


class View(dexterity.DisplayForm):
    """ sample view class """

    grok.context(Iagendamento)
    grok.require('zope2.View')

    def processaAgendamentos(self,ini,fin):
			
		colunas=[]
		dados=[]
				
		conjlinhas=self.context.saida.splitlines()		
		for coluna in conjlinhas[0].split(';'): 
			colunas.append(str(coluna).upper())
					
		inicial=int(ini)
		final=int(fin)
		
		if inicial<2:
			inicial=1
		
		if final>len(conjlinhas[1:])-1:
			final=len(conjlinhas[1:])-1
		
		for linha in conjlinhas[1:]:     	
			registros = linha.split(';')     
			listaDeDados=[]
			
			listaDeDados.append(registros[0].decode('iso-8859-1'))
			listaDeDados.append(registros[1])
			listaDeDados.append(int(registros[2]))
			listaDeDados.append(registros[3])
			listaDeDados.append(registros[4])
			listaDeDados.append(registros[5])
			listaDeDados.append(registros[6])
			listaDeDados.append(registros[7])
			listaDeDados.append(registros[8])
			listaDeDados.append(registros[9])
			listaDeDados.append(registros[10])
			listaDeDados.append(registros[11])			
			listaDeDados.append(registros[12])
			listaDeDados.append(registros[13])				
			
			dados.append(listaDeDados)      

		saida=sorted(dados, key=lambda dado: dado[1])		
		saida=sorted(saida, key=lambda dado: dado[12])
		saida=sorted(saida, key=lambda dado: dado[9])
		recorte=saida[inicial:final]
	
		return [colunas,recorte]
		
class Relatorio(dexterity.DisplayForm):
    """ sample view class """

    grok.context(Iagendamento)
    grok.require('zope2.View')

    def obtemData(self):		
		diaAtual = datetime.today()
		diasSemana = ['Segunda','Terca','Quarta','Quinta','Sexta','Sabado','Domingo']
		diaSemanaHoje=diasSemana[diaAtual.weekday()]
		strHoje = "Data: "+diaSemanaHoje+", "+str(diaAtual.day)+"/"+str(diaAtual.month)+"/"+str(diaAtual.year)
	
		return strHoje	
	
    def processaAgendamentos(self,ini,fin,hoje):
			
		colunas=[]
		dados=[]
				
		conjlinhas=self.context.saida.splitlines()		
		for coluna in conjlinhas[0].split(';'): 
			colunas.append(str(coluna).upper())
					
		inicial=int(ini)
		final=int(fin)
		
		
		if inicial<2:
			inicial=1
		
		if final>len(conjlinhas[1:])-1:
			final=len(conjlinhas[1:])-1
		
		for linha in conjlinhas[1:]:     	
			registros = linha.split(';')     
			listaDeDados=[]
			
			listaDeDados.append(registros[0].decode('iso-8859-1'))
			listaDeDados.append(registros[1])
			listaDeDados.append(int(registros[2]))
			listaDeDados.append(registros[3])
			listaDeDados.append(registros[4])
			listaDeDados.append(registros[5])
			listaDeDados.append(registros[6])
			listaDeDados.append(registros[7])
			listaDeDados.append(registros[8])
			listaDeDados.append(registros[9])
			listaDeDados.append(registros[10])
			listaDeDados.append(registros[11])			
			listaDeDados.append(registros[12])
			listaDeDados.append(registros[13])				
			
			dados.append(listaDeDados)      
			
		saida=sorted(dados, key=lambda dado: dado[1])
		saida=sorted(saida, key=lambda dado: dado[9])
		saida=sorted(saida, key=lambda dado: dado[12])		
		
			
		diaAtual = datetime.today()			
		diasSemana = ['Segunda','Terca','Quarta','Quinta','Sexta','Sabado','Domingo']
		diaSemanaHoje=diasSemana[diaAtual.weekday()]		
		resultado=[]
		if hoje:									
			for linha in saida:
				diaIDaLinha=datetime.strptime(linha[9], '%Y-%m-%d')				
				diaFDaLinha=datetime.strptime(linha[10], '%Y-%m-%d')				
				listaDiaslinha=linha[4].split('-')				
				if diaSemanaHoje in listaDiaslinha and diaAtual>=diaIDaLinha and diaAtual<=diaFDaLinha:
					resultado.append(linha)			
					
		recorte=resultado[inicial:final]
		
		return [colunas,recorte,inicial,final]
		
		
    def processaData(self,d):
		data= datetime.strptime(d, '%Y-%m-%d')
		saida=str(data.day)+"/"+str(data.month)+"/"+str(data.year)
		return saida
