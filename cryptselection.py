# -*- coding: utf-8 -*-

# Copyright 2015 Klaus Holler <kho@gmx.at>
# License:  same as zim (gpl)

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
			# TODO remove hardcoded recipient
			enccmd = '/usr/bin/gpg -ear kho@gmx.at --always-trust'
			cryptcmd = enccmd.split(" ")
			newtext = None
			p = Popen(cryptcmd, stdin=PIPE, stdout=PIPE)
			newtext, err = p.communicate(input=sel_text)
			if newtext is None:
				buffer.insert_at_cursor("cryptcmd '%s' failed - got '%s'" % (cryptcmd, err))
			else:	# delete selection only if crypt command was successful
				bounds = map(buffer.get_iter_at_offset, self_bounds)
				buffer.delete(*bounds)
				buffer.insert_at_cursor("\n%s\n" % newtext)
			# Replace selection
			#buffer.delete(iter_begin_line, iter_end_line)
			#for line in sorted_lines:
			#	buffer.insert_parsetree_at_cursor(line[1])
