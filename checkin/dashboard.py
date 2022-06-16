from sloth.app.dashboard import Dashboard
from .models import Aplicacao, Pessoa

class AppDashboard(Dashboard):
    
    def load(self, request):
        self.shortcuts(Aplicacao, Pessoa)
