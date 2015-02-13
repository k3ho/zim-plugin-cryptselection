zim-plugin-cryptselection
=========================

A plugin for Zim-Wiki_ which encrypts the current selection, replacing plaintext 
in a ZIM page by its encrypted representation. 

If a complete -----BEGIN PGP MESSAGE----- ... -----END PGP MESSAGE----- block is
selected then decrypt the block. For that to work the passphrase of the required
secret key has to be provided via a pinentry popup, i.e. the gpg-agent has to be
started before zim and has to be configured to display a pinentry popup.

Encryption and decryption commands to be used have to be configured once in 
the configuration dialog, use e.g. 

* as encryption command: '/usr/bin/gpg2 --always-trust -ear TheRecipientId'

* as decryption command: '/usr/bin/gpg2 -d'


The plugin may be installed (like all Zim-Plugins_) by cloning it to one of Zim's
plugin search directories, like ~/.local/share/zim/plugins on Linux:

  cd ~/.local/share/zim/plugins &&
  git clone https://github.com/k3ho/zim-plugin-cryptselection.git cryptselection

Zim plugin written by Klaus Holler (kho at gmx dot at)


.. _Zim-Wiki: http://www.zim-wiki.org/
.. _Zim-Plugins: https://github.com/jaap-karssenberg/zim-wiki/wiki/Plugins
