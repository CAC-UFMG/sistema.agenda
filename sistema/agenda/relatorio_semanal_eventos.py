from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.security import checkPermission
from datetime import datetime
from pytz import timezone



class relatorio_semanal_eventos(BrowserView):
    """ Render the title and description of item only (example)
    """
    index = ViewPageTemplateFile("resources/relatorio_semanal_eventos.pt")
	
    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
		
    def obtemEventosDaSemana(self):	
     pastaAgenda = self.context     
     result = []
     semana={}
     semana['0']=[]
     semana['1']=[]
     semana['2']=[]
     semana['3']=[]
     semana['4']=[]
     semana['5']=[]
     semana['6']=[]
     hoje=datetime.today()   
     vazio=True	 
     wf = getToolByName(pastaAgenda,'portal_workflow')     
     for evento in pastaAgenda.listFolderContents():        
        if checkPermission('sistema.agenda.visualizaEvento', evento) and evento.portal_type=='sistema.agenda.evento':            
            diaEvento=datetime(evento.start.year,evento.start.month,evento.start.day)
            diaFimEvento=datetime(evento.end.year,evento.end.month,evento.end.day)
            semanaEvento = diaEvento.isocalendar()[1]
            semanaFimEvento = diaFimEvento.isocalendar()[1]
            semanaHoje = hoje.isocalendar()[1]
            indicadorMesmaSemana = semanaEvento==semanaHoje or semanaFimEvento==semanaHoje
            horaEvento=evento.start.time()			
            horaEventoStr=str(evento.start.astimezone(timezone(evento.timezone)).time())
            local= ''
            estado = wf.getInfoFor(evento,'review_state')	 
            if evento.local is not None:
              for rel in evento.local:
                local = local+' - '+rel.to_object.title 
            else:
              local= 'sem local definido'
            
            if indicadorMesmaSemana and estado=='agendado':
              vazio=False
              resultado ={'titulo':evento.title.upper(),'local':local.title,'horario':horaEvento,'diaSemana':diaEvento.weekday(),'horarioStr':horaEventoStr,'link':evento.absolute_url}              
              if semanaFimEvento==semanaHoje and semanaEvento!=semanaHoje:
                ultimoDia=diaFimEvento.weekday()
                i=0
                while i<=ultimoDia:
                  semana[str(i)].append(resultado)
                  i+=1
              else:
                ultimoDia=diaFimEvento.weekday()
                primeiroDia=diaEvento.weekday()
                i=primeiroDia
                while i<=ultimoDia:
                  semana[str(i)].append(resultado)
                  i+=1                
        
     if not vazio:		   
       for i in semana.keys():
           semana[i]=sorted(semana[i],key=lambda evnt:evnt.values()[2])
     else:		 
       semana=[]  	 
     return semana
	 