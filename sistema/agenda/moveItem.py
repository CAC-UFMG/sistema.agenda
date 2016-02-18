from Acquisition import aq_inner, aq_parent

from Products.Five import BrowserView


class moveClass(BrowserView):
 def copiaParaPastaMae(self, state_change):
   pai = aq_parent(aq_inner(self))
   clipboard = pai.manage_cutObjects([self.id])
   dest = aq_parent(aq_inner(pai))
   result = dest.manage_pasteObjects(clipboard)
   print "executou"
   return "oi"