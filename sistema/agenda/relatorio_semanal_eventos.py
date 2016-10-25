from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.security import checkPermission
from datetime import datetime, timedelta
from pytz import timezone



class relatorio_semanal_eventos(BrowserView):
    """ Render the title and description of item only (example)
    """
    index = ViewPageTemplateFile("resources/relatorio_semanal_eventos.pt")
	
    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def obtemDiasDaSemana(self):	    
     dias = [0,0,0,0,0,0,0]
     
     hoje=datetime.today()   
     semanaHoje = hoje.isocalendar()[1]
	 
     umDia = timedelta(days=1)	 
     dDestaSemana = hoje.weekday()
     pD=0
     uD=6
     while pD <= uD:       
       if pD <=dDestaSemana:
         dEmQuestao = hoje-umDia*pD
         dias[dDestaSemana-pD]=str(dEmQuestao.day)+'/'+str(dEmQuestao.month)+'/'+str(dEmQuestao.year)	 
       else:
         dEmQuestao = hoje+umDia*(pD-dDestaSemana)
         dias[pD]=str(dEmQuestao.day)+'/'+str(dEmQuestao.month)+'/'+str(dEmQuestao.year)	 
       pD=pD+1
	   
	   
     return dias	
	  
    def obtemEventosDaSemana(self):	
     pastaAgenda = self.context     
     
     semana={}
     semana['0']=[]
     semana['1']=[]
     semana['2']=[]
     semana['3']=[]
     semana['4']=[]
     semana['5']=[]
     semana['6']=[]
	 
     hoje=datetime.today()   
     semanaHoje = hoje.isocalendar()[1]	 
     
     vazio=True	 
     wf = getToolByName(pastaAgenda,'portal_workflow')     
     for evento in pastaAgenda.listFolderContents():        
        if checkPermission('sistema.agenda.visualizaEvento', evento) and evento.portal_type=='sistema.agenda.evento':            
            diaEvento=datetime(evento.start.year,evento.start.astimezone(timezone(evento.timezone)).month,evento.start.astimezone(timezone(evento.timezone)).day)
            diaFimEvento=datetime(evento.end.year,evento.end.astimezone(timezone(evento.timezone)).month,evento.end.astimezone(timezone(evento.timezone)).day)
            semanaEvento = diaEvento.isocalendar()[1]
            semanaFimEvento = diaFimEvento.isocalendar()[1]            
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
            
            if indicadorMesmaSemana and (estado=='agendado' or estado=='terminado'):
              vazio=False
              resultado ={'titulo':evento.title.upper(),'local':local.title,'horario':horaEvento,'diaSemana':diaEvento.weekday(),'horarioStr':horaEventoStr,'link':evento.absolute_url}              
			  #Se o evento comecou antes e termina nessa semana
              if semanaFimEvento==semanaHoje and semanaEvento!=semanaHoje:
                ultimoDia=diaFimEvento.weekday()
                i=0
                while i<=ultimoDia:
                  semana[str(i)].append(resultado)
                  i+=1
			  #Se o evento eh da semana atual
              else:
                ultimoDia=diaFimEvento.weekday()
                primeiroDia=diaEvento.weekday()
                j=primeiroDia      
                if ultimoDia!=primeiroDia:    
                  while j<=ultimoDia:
                    semana[str(j)].append(resultado)
                    j+=1                
                else:                 
                  semana[str(primeiroDia)].append(resultado)                  
        
     if not vazio:		   
       for i in semana.keys():
           semana[i]=sorted(semana[i],key=lambda evnt:evnt['horario'])
     else:		 
       semana=[]  	 
     return semana
	 


	 
