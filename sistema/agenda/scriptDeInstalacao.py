from Products.CMFPlone.utils import _createObjectByType
from zope.component import getUtility
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY
from Products.ATContentTypes.lib import constraintypes
from Solgema.fullcalendar.interfaces import ISolgemaFullcalendarProperties
from Solgema.fullcalendar.browser.dx import InlineFrameAddView
from Solgema.fullcalendar import interfaces
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.permissions import setDefaultRoles

		
def criaPastas(context):
  raiz = context.getSite()  
  tiposinstalados = raiz.portal_types.listContentTypes()
  adicionais = ['sistema.agenda.membrodeequipe','sistema.agenda.local','sistema.agenda.evento']
  
  intersecao = [t for t in tiposinstalados if t in adicionais]
  intersecao.sort()
  adicionais.sort()
  if intersecao==adicionais:  
   if not raiz.get('agenda',None):
      raiz.plone_log("Criando pastas iniciais.")
      for item in raiz.listFolderContents(contentFilter={"portal_type":["Folder","Document"]}):
        raiz.manage_delObjects([item.getId()])
      _createObjectByType('Folder',raiz,id='agenda',title="Agenda")
      pastaAgenda=raiz.get('agenda')      
      _createObjectByType('Folder',pastaAgenda,id='preagenda',title="Pre Agendamentos")
      _createObjectByType('Folder',raiz,id='equipe',title="Equipe")
      _createObjectByType('Folder',raiz,id='locais',title="Locais")
      _createObjectByType('Collection',raiz,id='listagem',title="Listagem de eventos")
      
      
      pastaPreAgenda=pastaAgenda.get('preagenda')  
      pastaEquipe=raiz.get('equipe')      
      pastaLocais=raiz.get('locais')    
      listagem = raiz.get('listagem')	  
	  
      if pastaEquipe:
        _createObjectByType('sistema.agenda.membrodeequipe',pastaEquipe,id='ivanildo',title='Ivanildo',funcao='Tecnico de som',regime='30hs')
        _createObjectByType('sistema.agenda.membrodeequipe',pastaEquipe,id='Diano',title='Diano',funcao='Tecnico de som',regime='30hs')
        _createObjectByType('sistema.agenda.membrodeequipe',pastaEquipe,id='Alef',title='Alef',funcao='Tecnico de som',regime='30hs')
        _createObjectByType('sistema.agenda.membrodeequipe',pastaEquipe,id='Hector',title='Hector',funcao='Tecnico de som',regime='30hs')
        _createObjectByType('sistema.agenda.membrodeequipe',pastaEquipe,id='Alcindo',title='Alcindo',funcao='Tecnico de som',regime='30hs')
        _createObjectByType('sistema.agenda.membrodeequipe',pastaEquipe,id='Felipe',title='Felipe',funcao='Tecnico de som',regime='30hs')
  
      if pastaLocais:
        _createObjectByType('sistema.agenda.local',pastaLocais,id='saguao-reitoria',title='Saguao da Reitoria',unidade='Reitoria')
        _createObjectByType('sistema.agenda.local',pastaLocais,id='auditorio-reitoria',title='Auditorio da Reitoria',unidade='Reitoria')
        _createObjectByType('sistema.agenda.local',pastaLocais,id='gramado-reitoria',title='Gramado da Reitoria',unidade='Reitoria')
        _createObjectByType('sistema.agenda.local',pastaLocais,id='praca-servicos',title='Praca de Servicos',unidade='Reitoria')
        _createObjectByType('sistema.agenda.local',pastaLocais,id='auditorio-nobre',title='Auditorio Nobre do CAD 1',unidade='CAD1')
        _createObjectByType('sistema.agenda.local',pastaLocais,id='auditorio-um-cad-i',title='Auditorio 1 do Cad 1',unidade='CAD1')
        _createObjectByType('sistema.agenda.local',pastaLocais,id='auditorio-dois-cad-i',title='Auditorio 2 do Cad 1',unidade='CAD1')
        _createObjectByType('sistema.agenda.local',pastaLocais,id='auditorio-um-cad-ii',title='Auditorio 1 do Cad 2',unidade='CAD2')
        _createObjectByType('sistema.agenda.local',pastaLocais,id='auditorio-dois-cad-ii',title='Auditorio 2 do Cad 2',unidade='CAD2')
		


      from plone.formwidget.querystring.converter import QueryStringConverter
      a={"Type":"sistema.agenda.evento","review_state":"agendado" }
      #qc = QueryStringConverter()
      #listagem.query = qc.toWidgetValue(a)
      raiz.setLayout(listagem.id)
      listagem.setLayout("event_listing")	        
      pastaAgenda.setLayout("solgemafullcalendar_view")	  
      pastaEquipe.setLayout("folder_summary_view")
      pastaLocais.setLayout("folder_summary_view")
	  
	  
      workflowTool = getToolByName(raiz, "portal_workflow")
      workflowTool.doActionFor(pastaAgenda, "publish")      
      workflowTool.doActionFor(pastaLocais, "publish") 
      workflowTool.doActionFor(pastaEquipe, "publish") 
      workflowTool.doActionFor(listagem, "publish") 
      pastaAgenda.manage_permission('Add portal content',('Anonymous',))	  
      pastaAgenda.manage_permission('sistema.agenda: ModificaEvento',('Anonymous',))	   
      pastaAgenda.manage_permission('Delete objects',('Anonymous',))	  
      pastaPreAgenda.manage_permission('View management screens',('Anonymous',))
 
   
      campo= ISolgemaFullcalendarProperties(aq_inner(pastaAgenda), None)
      setattr(campo,'defaultCalendarView',u'month')
      setattr(campo,'eventType',u'sistema.agenda.evento')
      
	  
      mt = raiz.portal_membership
      regTool=raiz.portal_registration
      memTool=raiz.portal_membership
      loginSecretaria='agendador'
      senhaSecretaria='agendador'
      emailSecretaria='agendador@gmail.com'
      if mt.getMemberById(loginSecretaria) is None:
        memTool.addMember(loginSecretaria,senhaSecretaria,['Site Administrator'],[])

      manager = getUtility(IPortletManager, name='plone.leftcolumn', context=raiz)
      assignments = getMultiAdapter((raiz, manager), IPortletAssignmentMapping)
      for portlet in assignments:
        del assignments[portlet]
		
      manager = getUtility(IPortletManager, name='plone.rightcolumn', context=raiz)
      assignments = getMultiAdapter((raiz, manager), IPortletAssignmentMapping)
      for portlet in assignments:         
        if str(portlet)!='calendar':
          del assignments[portlet]	

      manager = getUtility(IPortletManager, name="plone.rightcolumn")
      blacklist = getMultiAdapter((raiz, manager), ILocalPortletAssignmentManager)
      blacklist.setBlacklistStatus(CONTEXT_CATEGORY, True)		  
	  
      manager = getUtility(IPortletManager, name="plone.rightcolumn")
      blacklist = getMultiAdapter((pastaAgenda, manager), ILocalPortletAssignmentManager)
      blacklist.setBlacklistStatus(CONTEXT_CATEGORY, True)
	  
      pastaEquipe.setConstrainTypesMode(constraintypes.ENABLED)
      pastaEquipe.setLocallyAllowedTypes(["sistema.agenda.membrodeequipe"])
      pastaEquipe.setImmediatelyAddableTypes(["sistema.agenda.membrodeequipe"])
	  
      pastaLocais.setConstrainTypesMode(constraintypes.ENABLED)
      pastaLocais.setLocallyAllowedTypes(["sistema.agenda.local"])
      pastaLocais.setImmediatelyAddableTypes(["sistema.agenda.local"])
      
      pastaAgenda.setConstrainTypesMode(constraintypes.ENABLED)
      pastaAgenda.setLocallyAllowedTypes(["sistema.agenda.evento"])
      pastaAgenda.setImmediatelyAddableTypes(["sistema.agenda.evento"])