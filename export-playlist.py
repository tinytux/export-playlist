from gi.repository import Gio, GLib, Gtk, GObject, Peas

import os
from urllib.parse import urlparse, unquote
import shlex

class ExportPlaylist(GObject.Object, Peas.Activatable):
	__gtype_name__ = 'ExportPlaylist'
	object = GObject.property(type=GObject.Object)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		action = Gio.SimpleAction(name='export-playlist')
		action.connect('activate', self.export)

		app = Gio.Application.get_default()
		app.add_action(action)

		menu_item = Gio.MenuItem()
		menu_item.set_label("Export..")
		menu_item.set_detailed_action('app.export-playlist')

		app.add_plugin_menu_item('playlist-menu', 'export-menu-item', menu_item)

	def do_deactivate(self):
		app = Gio.Application.get_default()
		app.remove_action('export-playlist')
		app.remove_plugin_menu_item('playlist-menu', 'export-menu-item')

	def export(self, action, data):
		shell = self.object
		page = shell.props.selected_page
		query_model = page.get_query_model()

		# urlparse to parse path from url scheme file://
		paths = [urlparse(row[0].get_playback_uri()).path for row in query_model]
		# decode: replace %xx escapes
		paths = [unquote(path) for path in paths]
		# cp SOURCEs
		src_cmdline = ' '.join(shlex.quote(uri) for uri in paths)


		dialog = Gtk.FileChooserDialog(None, None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			# cp DEST directory
			dest = unquote(urlparse(dialog.get_uri()).path)
			cmdline = 'cp ' + src_cmdline + ' ' + shlex.quote(dest)
			GLib.spawn_command_line_async(cmdline)
		dialog.destroy()



		
