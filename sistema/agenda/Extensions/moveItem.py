from Acquisition import aq_inner, aq_parent

def copiaParaPastaMae(self, state_change):
   pai = aq_parent(aq_inner(self))
   clipboard = pai.manage_cutObjects([self.id])
   dest = aq_parent(aq_inner(pai))
   result = dest.manage_pasteObjects(clipboard)
