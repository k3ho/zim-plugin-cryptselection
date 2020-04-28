# -*- coding: utf-8 -*-
# cryptselection plugin for zim
#
# Copyright 2015 Klaus Holler <kho@gmx.at>
# License:  same as zim (gpl)
#
# Installation/Usage:
# * Put the cryptselection/ directory to your ~/.local/share/zim/plugins subdirectory
#   i.e. cd ~/.local/share/zim/plugins &&
#        git clone https://github.com/k3ho/zim-plugin-cryptselection.git cryptselection
# * Then (re)start zim, and setup once the 'Crypt Selection' plugin:
#   * enable it in Edit>Preferences>Plugins and
#   * set the encryption/decryption commands via 'Configure' button
# * For in-place decryption gpg-agent should be started before starting zim and be
#   configured properly to display a pinentry popup to ask for the PGP key passphrase.

from __future__ import with_statement

from gi.repository import Gtk
import gtk
import re
from subprocess import Popen, PIPE
import shlex

from zim.plugins import PluginClass
from zim.actions import action

from zim.gui.pageview import PageViewExtension
from zim.formats import get_format

import logging

logger = logging.getLogger('zim.plugins.cryptselection')


class CryptSelectionPlugin(PluginClass):

    plugin_info = {
        'name': _('Crypt Selection'), # T: plugin name
        'description': _('''\
This plugin encrypts or decrypts the current selection 
with a specified encryption command (e.g. gpg).
If -----BEGIN PGP MESSAGE----- is found at selection
start and -----END PGP MESSAGE----- found at selection
end then decrypt, otherwise encrypt.
'''), # T: plugin description
        'author': 'Klaus Holler',
        'help': 'Plugins:Crypt Selection',
    }

    plugin_preferences = [
        # key, type, label, default
        ('encryption_command', 'string',
                _('Encryption Command (reads plaintext from stdin)'),
                '/usr/bin/gpg2 --always-trust -ear RECIPIENT'), # T: plugin preference
        ('decryption_command', 'string',
                _('Decryption Command (reads encrypted text from stdin)'),
                '/usr/bin/gpg2 -d'), # T: plugin preference
    ]


class CryptoSelectionPageViewExtension(PageViewExtension):

    plugin = None

    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)
        self.plugin = plugin

    @action(_('Cr_ypt selection'), menuhints='edit') # T: menu item
    def crypt_selection(self):
        buffer = self.pageview.textview.get_buffer()
        try:
            sel_start, sel_end = buffer.get_selection_bounds()
        except ValueError:
            msg = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE,
                                    _("Please select the text to be encrypted, first."))
            msg.run()
            msg.destroy()
                # T: Error message in "crypt selection" dialog, %s will be replaced
                # by application name
            return

        first_lineno = sel_start.get_line()
        last_lineno = sel_end.get_line()

        with buffer.user_action:
            assert buffer.get_has_selection(), 'No Selection present'
            sel_text = self.pageview.get_selection(format='wiki')
            self_bounds = (sel_start.get_offset(), sel_end.get_offset())
            if ((re.match(r'[\n\s]*\-{5}BEGIN PGP MESSAGE\-{5}', sel_text) is None) or
                re.search(r'\s*\-{5}END PGP MESSAGE\-{5}[\n\s]*$', sel_text) is None):
                # default is encryption:
                encrypt = True
                cryptcmd = shlex.split(self.plugin.preferences['encryption_command'])
            else:
                # on-the-fly decryption if selection is a full PGP encrypted block
                encrypt = False
                cryptcmd = shlex.split(self.plugin.preferences['decryption_command'])
            newtext = None
            p = Popen(cryptcmd, stdin=PIPE, stdout=PIPE)
            newtext, err = p.communicate(input=sel_text.encode())
            if p.returncode == 0:
                # replace selection only if crypt command was successful
                # (incidated by returncode 0)
                if encrypt is True:
                    bounds = map(buffer.get_iter_at_offset, self_bounds)
                    buffer.delete(*bounds)
                    buffer.insert_at_cursor("\n%s\n" % newtext.decode())
                else:
                    # replace selection with decrypted text
                    parser = get_format('wiki').Parser()
                    tree = parser.parse(newtext.decode())
                    with buffer.user_action:
                        bounds = map(buffer.get_iter_at_offset, self_bounds)
                        buffer.delete(*bounds)
                        buffer.insert_parsetree_at_cursor(tree,interactive=True)

            else:
                logger.warn("crypt command '%s' returned code %d." % (cryptcmd,
                            p.returncode))

# :mode=python:tabSize=4:indentSize=4:noTabs=true:wrap=soft:maxLineLen=90:
