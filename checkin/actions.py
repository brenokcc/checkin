from sloth import actions


class SincronizarFoto(actions.Action):
    class Meta:
        icon = 'arrow-repeat'
        verbose_name = 'Sincronizar Foto'
        modal = True
        style = 'primary'

    def submit(self):
        self.instance.sincronizar_foto()
        super().submit()


class ResetarDispositvo(actions.Action):
    class Meta:
        icon = 'phone'
        verbose_name = 'Resetar Dispositivo'
        modal = True
        style = 'warning'

    def submit(self):
        self.instance.resetar_dispositivo()
        super().submit()