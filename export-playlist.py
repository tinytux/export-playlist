from gi.repository import Gio, Gtk, GObject, Peas

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
		print("Exporting Playlist...")
		shell = self.object
		# GtkTreeStore
		display_page_model = shell.props.display_page_model.props.child_model
		# Gtk.TreeModelRow
		playlist = [x for x in display_page_model if x[1].props.id == "playlists"][0]
		playlist_iter = playlist.iterchildren()
		for i in playlist_iter:
			playlist_source = i[1]
			print(playlist_source)





		
