#
# This file is part of ibus-bogo project.
#
# Copyright (C) 2012 Long T. Dam <longdt90@gmail.com>
# Copyright (C) 2012-2013 Trung Ngo <ndtrung4419@gmail.com>
# Copyright (C) 2013 Duong H. Nguyen <cmpitg@gmail.com>
# Copyright (C) 2013 Hai P. Nguyen <hainp2604@gmail.com>
# Copyright (C) 2013-2014 Hai T. Nguyen <phaikawl@gmail.com>
#
# ibus-bogo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ibus-bogo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ibus-bogo.  If not, see <http://www.gnu.org/licenses/>.
#

from gi.repository import IBus
import os
import sys

ENGINE_PATH = os.path.dirname(__file__)
sys.path.append(
    os.path.abspath(os.path.join(ENGINE_PATH, "..")))


from mouse_detector import MouseDetector
from ui import UiDelegate
from direct_backend import DirectEditBackend


class Engine(IBus.Engine):
    __gtype_name__ = 'EngineBoGo'

    def __init__(self, config, abbr_expander):
        super(Engine, self).__init__()

        self.config = config
        self.ui_delegate = UiDelegate(engine=self)
        self.backend = DirectEditBackend(engine=self,
                                         config=config,
                                         abbr_expander=abbr_expander)

        # Create a new thread to detect mouse clicks
        mouse_detector = MouseDetector.get_instance()
        mouse_detector.add_mouse_click_listener(self.reset)

        self.input_context_capabilities = 0
        self.reset()

    def reset(self):
        self.backend.reset()

    # The "do_" part denotes a default signal handler
    def do_process_key_event(self, keyval, keycode, modifiers):
        """Implement IBus.Engine's process_key_event default signal handler.

        Args:
            keyval - The keycode, transformed through a keymap, stays the
                same for every keyboard
            keycode - Keyboard-dependant key code
            modifiers - The state of IBus.ModifierType keys like
                Shift, Control, etc.
        Return:
            True - if successfully process the keyevent
            False - otherwise

        This function gets called whenever a key is pressed.
        """

        # Ignore key release events
        event_is_key_press = (modifiers & (1 << 30)) == 0

        # There is a strange overflow bug with python3-gi here so the above
        # line is used instead
        # is_press = ((modifiers & IBus.ModifierType.RELEASE_MASK) == 0)

        if not event_is_key_press:
            return False

        return self.backend.process_key_event(keyval, modifiers)

    def do_enable(self):
        self.ui_delegate.do_enable()
        self.backend.do_enable()

    def do_disable(self):
        self.reset()

    def do_focus_in(self):
        self.backend.do_focus_in()

    def do_focus_out(self):
        self.reset()

    def do_property_activate(self, prop_key, state):
        self.ui_delegate.do_property_activate(prop_key, state)

    def do_set_capabilities(self, caps):
        self.input_context_capabilities = caps
