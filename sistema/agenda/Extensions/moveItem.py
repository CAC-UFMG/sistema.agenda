from Acquisition import aq_inner, aq_parent
from zope.lifecycleevent import modified

def copiaParaPastaMae(self, state_change):   
   pai = aq_parent(aq_inner(state_change.object))
   clipboard = pai.manage_cutObjects([state_change.object.id])
   dest = aq_parent(aq_inner(pai))
   result = dest.manage_pasteObjects(clipboard)
   
def reindexa(self, state_change):      
   obj = state_change.object
   modified(obj)
   #obj.reindexObject(idxs=["review_state"])