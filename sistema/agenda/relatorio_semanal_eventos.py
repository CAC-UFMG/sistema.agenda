from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from datetime import datetime
from zope.intid.interfaces import IIntIds


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
     intids= getUtility(IIntIds)
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
     for evento in pastaAgenda.listFolderContents():        
        if checkPermission('sistema.agenda.visualizaEvento', evento):            
            diaEvento=datetime(evento.start.year,evento.start.month,evento.start.day)
            semanaEvento = diaEvento.isocalendar()[1]
            semanaHoje = hoje.isocalendar()[1]
            indicadorMesmaSemana = semanaEvento==semanaHoje
            horaEvento=evento.start.time()
            horaEventoStr=str(horaEvento)
            local= ''
            if evento.local is not None:
              for rel in evento.local:
                local = local+' - '+rel.to_object.title 
            else:
              local= 'sem local definido'
            
            if indicadorMesmaSemana:
			  resultado ={'titulo':evento.title.upper(),'local':local.title,'horario':horaEvento,'diaSemana':diaEvento.weekday(),'horarioStr':horaEventoStr,'link':evento.absolute_url}
			  semana[str(diaEvento.weekday())].append(resultado)
     for i in semana.keys():
       semana[i]=sorted(semana[i],key=lambda evnt:evnt.values()[2])            
     return semana
	 