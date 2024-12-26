class Videoslot:
	
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp		
		self.cacheSource = None
		self.videoSource = None
		self.beatSource = None
		
		# setting main target OPs
		self.refreshTimer = self.ownerComp.op('refresh_timer')
		self.beat = self.ownerComp.op('beat1')
		self.selector = self.ownerComp.op('select1')
		self.beatselector = self.ownerComp.op('select2')
		self.videoSwitch = self.ownerComp.op('switch1')
		self.video = self.ownerComp.op('moviefilein1')
		self.fileList = op.LOOPER.op('grid_new/source')
	
	def SetCacheInput(self):
		#Sets the source input from the last cache
		self.cache = str(op.LOOPER.GetCache()) + "/cacheselect"
		self.selector.par.top = self.cache
		self.beatSource = str(op.LOOPER.GetCache()) + "/beat_replay"
		self.beatselector.par.chop = self.beatSource
		
		# debug
		print(self.ownerComp.name, 'takes in cache from', self.cache)		
		return
		
	def GetVideoInput(self):
		self.videoSource = op.LOOPER.fetch("last_location")
		
		# debug
		print(self.ownerComp.name, 'video source is', self.videoSource)
		
		self.ownerComp.store('location', self.videoSource)		
		return self.videoSource
	
	

		
	def Synchronize(self):
		# it should react only to wait_for_upd == 1
		# resets the cue to sync video cue with main beat
		# signalizing that the video is saved and ready to use
		self.beat.par.resetpulse.pulse()
		
		# try to fix here: pulse reload video
		self.video.par.reloadpulse.pulse()
		
		self.SwitchView(2)
		
		# letting the looper know that the video is saved
		op.LOOPER.SetCacheState("saved")		
		
		# debug:
		print(self.ownerComp.name, "is synced, cache is recorded")
		
		return
		
	def BeatReset(self):		
		self.beat.par.resetpulse.pulse()
		
		# debug:
		print(self.ownerComp.name, 'beat reset')
		
		return
	
	def SwitchView(self, videoSwitch):
		# switching the index of the input (none, cache, video)
		if videoSwitch > -1 and videoSwitch < 3:
			self.videoSwitch.par.index = videoSwitch
			
		# debug:
		print(self.ownerComp.name, 'view switched to', videoSwitch)
						
		return	
		
	def Clear(self):
		self.SwitchView(0)
		self.video.par.file = ''
		self.video.unload() 
		self.ownerComp.store('wait_for_upd', 0)				
		
		# debug:
		print(self.ownerComp.name, 'is clear')
		
		return
		
	def LoadRandom(self, seed = 1):
		self.SwitchView(2)
		#print(self.fileList[1,1])
		self.seed = seed
		file = self.fileList[(1+(int(tdu.rand(absTime.seconds + self.seed)*(self.fileList.numRows-1)))),1]
		self.video.par.file = file
		self.ownerComp.store('wait_for_upd', 0)
		self.SetLength()
		#self.WaitForSave(0)
		
		# debug:
		print(self.ownerComp.name, 'loaded random', file)
		
		pass
		
	def PutRecordedVideo(self):
		# method for putting the recorded video into a slot		
		# important to check the cache state
		
		state = op.LOOPER.GetCacheState()
		
		# case when it's nothing yet to put
		if state  == "empty" or state == "recorded":
			print('nothing to put, cache is', state)			
			
		# case for putting the cache that will be replaced with video
		elif state == "saving" or state == "saved":
			self.SetCacheInput()			
			self.SwitchView(1)
			self.WaitForSave(toggleDelay = 1, beatsDelay = 4)
			
			self.video.par.file = op.LOOPER.fetch('last_location')
			
			op.LOOPER.op('previewer2/select2').par.top = self.ownerComp.op('out1')
			

			
			pass
		
		# case for putting only the already saved video
		# elif state == "saved":
			#self.SwitchView(2)	
			#self.video.par.file = self.GetVideoInput()
			#pass		

		
	def WaitForSave(self, toggleDelay = 0, beatsDelay = 0):
		# prepares for syncing the recorded video 
		# after selection and recording
		# upd, the timer will run and check if the video 
		# is really saved				
		
		self.ownerComp.store('wait_for_upd', 0)				
		
		self.beat.par.period = self.SetLength()		
		self.beatsDelay = beatsDelay
		self.toggleDelay = toggleDelay		
		
		self.delay = op.LOOPER.GetDelay(0) * self.toggleDelay		
		#op.LOOPER.StartTimer(self.refreshTimer, 0, self.delay)
		op.LOOPER.StartTimer(self.refreshTimer, self.SetLength(), self.delay)
		
		# debug
		print(self.ownerComp.name, "waits for saving")
		
		pass
	
	def SetLength(self):
		length = op.LOOPER.CutFragment(self.video.par.file, '--', 'b.')
		self.beat.par.period = length
		
		# debug:
		# print(self.ownerComp.name, 'length is', length)
		
		return length				
	
	


	


		