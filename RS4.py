from gi.repository import GObject, RB, Peas
from re import search
import S4

class RS4 (GObject.Object, Peas.Activatable):
	object = GObject.property(type=GObject.Object)
	__gtype_name = 'RS4'

	def __init__(self):
		super(RS4, self).__init__()

	def do_activate(self):
		print("RadioScrobbler4 is Active!")
		while S4.get_session() is None:
			self.session=S4.get_session()
		self.shell = self.object
		self.player = self.shell.props.shell_player
		self.pc_id = self.player.connect('playing-changed', self.playing_changed)
		self.psc_id = self.player.connect('playing-song-changed', self.playing_song_changed)
		self.pspc_id = self.player.connect('playing-song-property-changed', self.playing_song_property_changed)
		self.current_entry=self.old_title=self.current_location=self.current_radio=self.current_title=None  #Del in deactivate check
		if self.player.get_playing()[1]:	#If a track is already playing while the plugin is activated, set entry
			print ("Track is already playing")
			self.set_entry(self.player.get_playing_entry())

	def do_deactivate(self):
		self.player.disconnect(self.pc_id)
		self.player.disconnect(self.psc_id)
		self.player.disconnect(self.pspc_id)
		self.current_entry=self.old_title=self.current_location=self.current_radio=self.current_title=None
		self.player = None
		del self.shell

	def playing_changed(self,player,playing):
		if playing:
			print ("Playing")
			self.set_entry(player.get_playing_entry())
		else:
			self.current_entry= None
			print("Not Playing")

	def playing_song_changed(self,player,entry):
		if player.get_playing()[1]:
			print("Playing Song Changed")
			self.set_entry(entry)

	def playing_song_property_changed(self, player, uri,property, old, new):
		if player.get_playing()[1] and property in ('title', 'rb:stream-song-title'):
			print("Playing Props Changed")
			self.current_title=new
			self.set_status()

	def set_entry(self,entry):		#Set current entry from new entry
		if entry==self.current_entry:   #If entry is the same as the current one
			return
		self.current_entry=entry	#Set new entry as the current one
		if entry is None:			#Entry is none when track is not playing
			return
		self.set_status_from_entry()

	def set_status_from_entry(self):		#Sets status from the current entry
		db=self.shell.get_property("db")
		self.current_location=self.current_entry.get_string(RB.RhythmDBPropType.LOCATION)   #File Location, which means url for a radio entry
		if not search('^file', self.current_location):			#If not playing a file then it must be radio url!
			self.current_radio=self.current_entry.get_string(RB.RhythmDBPropType.TITLE)   #Name of the station
			genre=self.current_entry.get_string(RB.RhythmDBPropType.GENRE)
			self.current_title=db.entry_request_extra_metadata(self.current_entry, 'rb:stream-song-title')
			print(bcolors.HEADER+"Radio: %s Genre: %s Location: %s"%(self.current_radio,genre,self.current_location)+bcolors.ENDC)
			self.set_status()

	def set_status(self):				#Sets status from current title
		if self.old_title!=self.current_title and self.current_title:   #Make sure track name changed and it is not Null
			print(bcolors.HEADER+"♫ %s ♫ "%(self.current_title)+bcolors.ENDC)
			#self.core()
			self.old_title=self.current_title		#Sets current title as old title

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	BADBLUE = '\033[96m'
	GREY = '\033[90m'
	ENDC = '\033[0m'

	def disable(self):
		self.HEADER = ''
		self.OKBLUE = ''
		self.OKGREEN = ''
		self.WARNING = ''
		self.FAIL = ''
		self.ENDC = ''	

