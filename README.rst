zim-plugin-cryptselection
=========================

A plugin for Zim-Wiki_ which encrypts the current selection, replacing plaintext 
in a ZIM page by its encrypted representation.

The encryption command to be used has to be configured once in the configuration
dialog, use e.g. '/usr/bin/gpg --always-trust -ear TheRecipientId'

The plugin may be installed (like all Zim-Plugins_) by cloning it to one of Zim's
plugin search directories, like ~/.local/share/zim/plugins on Linux:

  cd ~/.local/share/zim/plugins &&
  git clone https://github.com/k3ho/zim-plugin-cryptselection.git cryptselection

Zim plugin written by Klaus Holler (kho at gmx dot at)


.. _Zim-Wiki: http://www.zim-wiki.org/
.. _Zim-Plugins: https://github.com/jaap-karssenberg/zim-wiki/wiki/Plugins
