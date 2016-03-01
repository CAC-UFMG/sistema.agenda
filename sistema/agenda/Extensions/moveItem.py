from Acquisition import aq_inner, aq_parent
from zope.lifecycleevent import modified
from Products.CMFCore.utils import getToolByName

def copiaParaPastaMae(self, state_change):      
   pai = aq_parent(aq_inner(state_change.object))
   obj = state_change.object
   wf = getToolByName(obj,'portal_workflow')
   estado = wf.getInfoFor(obj,'review_state')
   #indo para a reserva, copia para agenda
   if pai.id == 'preagenda' and estado=='agendado':
     clipboard = pai.manage_cutObjects([obj.id])
     dest = aq_parent(aq_inner(pai))
     result = dest.manage_pasteObjects(clipboard)	 
     modified(result)
   
def reindexa(self, state_change):      
   obj = state_change.object
   modified(obj)   
