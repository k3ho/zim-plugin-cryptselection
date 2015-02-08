# -*- coding: utf-8 -*-

# Copyright 2015 Klaus Holler <kho@gmx.at>
# License:  same as zim (gpl)
#
# TODO support on-the-fly decryption, too,
#      if ------BEGIN PGP MESSAGE------ ... ------END PGP MESSAGE------ is selected.

from __future__ import with_statement

import gtk
from subprocess import Popen, PIPE

from zim.plugins import PluginClass, extends, WindowExtension
from zim.actions import action
from zim.gui.widgets import ui_environment, MessageDialog

import logging

logger = logging.getLogger('zim.plugins.cryptselection')


class CryptSelectionPlugin(PluginClass):

	plugin_info = {
		'name': _('Crypt Plugin'), # T: plugin name
		'description': _('''\
This plugin encrypts or decrypts the current selection 
with a specified encryption command (e.g. gpg).
'''), # T: plugin description
		'author': 'KlausHoller',
		'help': 'Plugins:Crypt Selection',
	}

	plugin_preferences = [
		# key, type, label, default
		('encryption_command', 'string', _('Encryption Command (reads plaintext from stdin)'), 
				'/usr/bin/gpg --always-trust -ear RECIPIENT'), # T: plugin preference
		# TODO
		#('decryption_command', 'string', _('Decryption Command (reads encrypted text from stdin)'), '/usr/bin/gpg'), # T: plugin preference
	]


@extends('MainWindow')
class MainWindowExtension(WindowExtension):

	uimanager_xml = '''
	<ui>
		<menubar name='menubar'>
			<menu action='edit_menu'>
				<placeholder name='plugin_items'>
					<menuitem action='crypt_selection'/>
				</placeholder>
			</menu>
		</menubar>
	</ui>
	'''

	def __init__(self, plugin, window):
		WindowExtension.__init__(self, plugin, window)
		self.preferences = plugin.preferences

	@action(_('Cr_ypt selection')) # T: menu item
	# TODO: add stock parameter to set icon
	def crypt_selection(self):
		buffer = self.window.pageview.view.get_buffer()
		try:
			sel_start, sel_end = buffer.get_selection_bounds()
		except ValueError:
			MessageDialog(self.ui,
				_('Please select the text to be encrypted, first.')).run()
				# T: Error message in "crypt selection" dialog, %s will be replaced by application name
			return

		first_lineno = sel_start.get_line()
		last_lineno = sel_end.get_line()

		with buffer.user_action:
			assert buffer.get_has_selection(), 'No Selection present'
			sel_text = self.window.pageview.get_selection(format='wiki')
			self_bounds = (sel_start.get_offset(), sel_end.get_offset())
			cryptcmd = self.preferences['encryption_command'].split(" ")
			newtext = None
			p = Popen(cryptcmd, stdin=PIPE, stdout=PIPE)
			newtext, err = p.communicate(input=sel_text)
			if p.returncode == 0:
				# replace selection only if crypt command was successful (incidated by returncode 0)
				bounds = map(buffer.get_iter_at_offset, self_bounds)
				buffer.delete(*bounds)
				buffer.insert_at_cursor("\n%s\n" % newtext)
			else:
				logger.warn("crypt command '%s' returned code %d." % (cryptcmd, p.returncode))
