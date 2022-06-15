from sloth import actions


class SincronizarFoto(actions.Action):
    class Meta:
        verbose_name = 'Sincronizar Foto'
        modal = True
        style = 'primary'

    def submit(self):
        self.instance.sincronizar_foto()
        super().submit()
