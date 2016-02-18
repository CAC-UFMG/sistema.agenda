from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class newEv(BrowserView):
    """ Render the title and description of item only (example)
    """
    index = ViewPageTemplateFile("evento_templates/newev.pt")
	
    def render(self):
        return self.index()

    def __call__(self):
        return self.render()