import settings
from directive import Directive


class ItemToggle(Directive):
    def __init__(self, item, *args, **kwargs):
        super(ItemToggle, self).__init__(*args, **kwargs)
        self.item = item
        self.arrangeable = False
        self._x = 0
        self.static = True

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return settings.SCREEN_HEIGHT - 1

    def complete(self):
        super(ItemToggle, self).complete()
        self.item.toggle()
        self.change_text(self.item.get_toggle_text())


class ItemGrab(Directive):

    range = 2

    def complete(self):
        self.game.player.inventory.pick_up_item(self.anchor)
        super(ItemGrab, self).complete()

