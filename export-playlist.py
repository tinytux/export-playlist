from __future__ import print_function
import sys

from gi.repository import Gio, GLib, Gtk, GObject, Peas, RB
import os
from urllib.parse import urlparse, unquote_plus, urljoin
from urllib.request import pathname2url, url2pathname


DEFAULT_PLAYLIST_PATH_PREFIX = "7E0A-B4E5/Music"

def print_debug(*args, **kwargs):
    #print(*args, file=sys.stderr, **kwargs)
    return 0

def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    return 0

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
        menu_item.set_label("Export Files To...")
        menu_item.set_detailed_action('app.export-playlist')

        app.add_plugin_menu_item('playlist-menu', 'export-menu-item', menu_item)

    def do_deactivate(self):
        app = Gio.Application.get_default()
        app.remove_action('export-playlist')
        app.remove_plugin_menu_item('playlist-menu', 'export-menu-item')

    def get_playlist_path_prefix(self):
        msg = 'The optional prefix will be added to all file names in the .m3u playlist.\nThe prefix is usually the path to the Music folder on your external SD card:'
        dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, msg)
        dialog.set_title('Playlist path prefix')

        box = dialog.get_content_area()
        userEntry = Gtk.Entry()
        userEntry.set_text(DEFAULT_PLAYLIST_PATH_PREFIX)
        userEntry.set_size_request(120, 0)
        box.pack_end(userEntry, False, False, 0)

        dialog.show_all()
        response = dialog.run()
        path_prefix = userEntry.get_text()
        dialog.destroy()
        return path_prefix

    def export(self, action, data):
        shell = self.object
        page = shell.props.selected_page
        query_model = page.get_query_model()

        library = Gio.Settings.new("org.gnome.rhythmbox.rhythmdb")

        library_location = library['locations'][0]
        print_debug(str(library_location))

        playlist_name = shell.get_property("selected_page").props.name
        uris = [row[0].get_playback_uri() for row in query_model]
        artists = [row[0].get_string(RB.RhythmDBPropType.ARTIST) for row in query_model]

        dialog = Gtk.FileChooserDialog(title="Select Folder",
            parent=shell.props.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            playlist_path_prefix = self.get_playlist_path_prefix()
            dest_dir = Gio.File.new_for_uri(dialog.get_uri())
            playlist_file = open('' + dest_dir.get_path() + '/' + playlist_name + '.m3u' ,'w')
            playlist_file.write('#EXTM3U\n')

            for uri in uris:
                source_file = Gio.File.new_for_uri(uri)
                fname_source = unquote_plus(urlparse(uri).path)

                fname_dest = unquote_plus(uri.replace(library_location, dest_dir.get_path()))
                print_debug(str(' '))

                dest_name = urljoin('file:', pathname2url(fname_dest))

                dest_file = Gio.File.new_for_uri(dest_name)
                print_debug('   source      = {src}'.format(src=fname_source))
                print_debug('   destination = {src}'.format(src=fname_dest))

                target_path = os.path.dirname(fname_dest)
                #print_debug('   path        = {p}'.format(p=target_path))
                if not os.path.exists(target_path):
                    os.makedirs(target_path)

                fname_dest_without_path = unquote_plus(uri.replace(library_location, playlist_path_prefix))

                if not os.path.isfile(fname_dest) and not os.path.islink(fname_dest):
                    print_debug('   link: {src} -> {dest}'.format(src=fname_source, dest=fname_dest))
                    try:
                        os.link(fname_source, fname_dest)
                        playlist_file.write('{fileName}\n'.format(fileName=fname_dest_without_path))
                    except:
                        print_error('skipping {src} -> {dest}'.format(src=fname_source, dest=fname_dest))
                        pass

            playlist_file.close()


            msg = 'Playlist "{playlist}.m3u" exported to directory {dir}'.format(playlist=playlist_name, dir=dest_dir.get_path())
            msgDialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, msg)
            msgDialog.run()
            msgDialog.destroy()

        dialog.destroy()

