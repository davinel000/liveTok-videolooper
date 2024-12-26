class VideoLooper:

	# State machine dictionary
	state_machine = {
    	1:	"StartupState",
    	2:	"WaitForRecState",
    	3:	"CountdownState",
    	4:	"RecState",
    	5:	"DecideState",
    	6:	"SelectSlotState",
    	7:	"ThankYouState"
	} 

### State Machine
	
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp		

		# setting variables and operators
		self.timer = op('timer_record')			
		self.animation_timer1 = op('control_panel/animation_timer')		
		self.thank_you_time = 180 #msec
	 
	def SetState(self, state):
		self.state = state
		self.current_state = self.state_machine[state]
		self.ownerComp.store('state', self.current_state)
		self.ownerComp.store('state_key', self.state)
		
		state_method = getattr(self, self.state_machine[self.state])
		state_method()
		
		# debug
		print('set state to', self.current_state)
		
	def GetState(self):
		self.state = self.ownerComp.fetch('state')
		return self.state
		
	def GetStateKey(self):
		self.key = self.ownerComp.fetch('state_key',1)
		return self.key			

	def StartupState(self): #1
		op.SOUND.Play(0,1,1,0,0) # only topline plays
		self.Replay(1)
		self.SwitchReplay(0)
		
		#starting animation (should be updated)
		self.StartTimer(self.animation_timer1,0,self.GetDelay(8))
				
		# setting cache state to "empty"
		self.SetCacheState("empty")
		

	def WaitForRecState(self): #2
		op.SOUND.Play(1,1,1,1,0) # everything plays except metro
		self.Replay(1)
		self.SwitchReplay(0)
		
		


	def CountdownState(self): #3
		op.SOUND.Play(0,1,1,1,1) # metronome and all except drums
		self.Record(1)
		self.Countdown()
		self.Replay(0)
		self.SwitchReplay(0)
		
		# self.TransitionTo(State.REC)

	def RecState(self): #4
		op.SOUND.Play(1,1,1,1,0) # everything plays except metro		
		#self.Record(1)
		self.Replay(0)
		self.SwitchReplay(0)
				
		# Add your TouchDesigner logic here
		# self.TransitionTo(State.DECIDE)

	def DecideState(self): #5
		op.SOUND.Play(1,1,1,1,0) # everything plays except metro		
		self.Record(0)
		self.Replay(1)
		self.SwitchReplay(1)
		
		# Add your TouchDesigner logic here
		# self.TransitionTo(State.SELECTSLOT)

	def SelectSlotState(self): #6
		op.SOUND.Play(1,1,1,1,0) # everything plays except metro
		
		# this state doesn't save the video
		# it should be done automatically
		
		if self.GetCacheState != 'saving':
			print('cache recording is not saved!')	
		
		self.Replay(1)
		self.SwitchReplay(0)
		return

	def ThankYouState(self): #7
		op.SOUND.Play(1,1,1,1,0) # everything plays except metro
		print("Entering THANKYOU state.")
		self.Replay(1)
		self.SwitchReplay(0)
		
		run("op.LOOPER.SetState(2)", delayFrames = self.thank_you_time)
		
				
		

###

	# Original functions rewritten as class methods with capitalized names
	
	# Controlling cache
	def SetCache(self, value):
		caches = [op('cache1'), op('cache2')]
		cache = caches[value]
		self.ownerComp.store('cache', cache)
		self.ownerComp.store('cachenum', value)
		self.ownerComp.store('length', self.ownerComp.par.Length)
		print('cache set to', cache)
		return cache
		
	def SetCacheState(self, value = "empty"):
		#cache states:
		## "empty" - the sketch is started, before beginning of the recording, when we pressed delete
		## "recorded" - the recording ended, but the file is not yet available (saved)
		## "saving" - we initiated saving, but the file is not saved yet
		## "saved" - when the file is saved and we can use it instead of cache
		## the current idea:
		## delete and save buttons trigger changes in cache state, and not just states themselves
				
		self.ownerComp.store('cachestate', value)
		print('cache state is set to', value)
		
	def GetCacheState(self):
		return self.ownerComp.fetch('cachestate')	

	def GetCache(self):
		return self.ownerComp.fetch('cache', op('cache1'))

	def GetCacheNum(self):
		return self.ownerComp.fetch('cachenum', 0)
	
# ----------------------------------------
	# Controlling looper methods
	
	
	def Countdown(self):
		# beginning the timer with delay and length pars
		self.StartTimer(self.timer, self.GetDelay(), self.GetFrameLength())
		pass
	
	def Record(self, value):
		# record operation
		
		length = self.ownerComp.par.Length
		
		print('recording is', value)
		
		# this is strange:
		recorder = self.GetCache().op('cache_record')
		
		if value == 1:
			if self.GetCache() is None or self.GetCacheNum() is None:
				self.SetCache(0)
				print('setting default cache')
			
			# switching the cache
			else:
				self.SetCache(1 - self.GetCacheNum())
			
			# selecting and setting up a recorder op from a proper cache
			recorder = self.GetCache().op('cache_record')
			recorder.par.cachesize = self.GetFrameLength()
			recorder.par.resetpulse.pulse()
			
			# setting the cache state to empty
			self.SetCacheState('empty')
			
			# beginning the timer with delay and length pars
			# self.StartTimer(self.timer, self.GetDelay(), self.GetFrameLength())
		
		# reaction to the end of recording
		if value == 0:
			self.ownerComp.par.Record = 0
			
			# setting the cache state to recorded
			self.SetCacheState('recorded')						

		recorder.par.active = value		 
		

	def Replay(self, value):
		# initiate or deinitiate replay
		player = self.GetCache().op('cacheselect')
		beat = self.GetCache().op('beat_replay')
		beat.par.reset = 1 - value
		beat.par.period = self.ownerComp.par.Length
		op('switch_cache').par.index = self.GetCacheNum()
		return

	def SwitchReplay(self, switch):
		# show either direct video or cached replay
		switcher = op('switch_replay')
		switcher.par.index = switch
		print('switched replay to', switch)
		return

	def GetDelay(self, min_delay=None, beat_op=None):
		# how many seconds to wait before the next n beats
		if min_delay is None:
			min_delay = self.ownerComp.par.Mindelay
		if beat_op is None:
			beat_op = op(self.ownerComp.par.Mainbeat)
		if (beat_op and beat_op.type == 'beat' and beat_op.par.bpm and beat_op.par.beat and beat_op.par.rampbeat):
			if min_delay is not None:
				current_beat = beat_op['beat']
				beats_per_bar = 4
				time_per_beat = 60.0 / float(op(beat_op)['bpm'])
				remaining_beats = beats_per_bar - (current_beat % beats_per_bar) - beat_op['rampbeat'] + min_delay
				time_until_next_bar = remaining_beats * time_per_beat
				return time_until_next_bar
		else:
			print('check beat operator: reference and activated outputs')
			return 0

	def StartTimer(self, timer, delay=0, length=1):
		# begin any selected timer with a preset delay and length
		if timer is not None and timer.type == 'timer':
			timer.par.delay = delay
			timer.par.length = length
			timer.par.initialize.pulse()
			print(f"timer {timer.name} will fire in {round(delay, 2)} sec")
			timer.par.start.pulse()
		else:
			print('check referenced timer')
		return 

	def GetFrameLength(self, length_in_beats=None, beat_op=None):
		# how many frames are in the selected number of beats
		if length_in_beats is None:
			length_in_beats = self.ownerComp.par.Length
		if beat_op is None:
			beat_op = op(self.ownerComp.par.Mainbeat)
		if length_in_beats is not None and beat_op is not None and beat_op.type == 'beat' and beat_op.par.bpm:
			duration = 60 / beat_op['bpm'] * project.cookRate * length_in_beats
			return duration
		else:
			print('no length to output, check length and beat_op settings')
			return

	def BeatReset(self, beatop = None):
		# resetting the main beat
		if beatop is None:
			beatop = op(self.ownerComp.par.Mainbeat)
		if beatop is not None and beatop.type == 'beat':
			beatop.par.resetpulse.pulse()
		return

	def SaveVideo(self):
		# just sending a command to save the video
		op('quick_saver').par.Save.pulse()
		
		# setting the state to "saving"
		self.SetCacheState("saving")
		
		return
	
# ----------------------------------------
	# Additional service methods
	
	def WinClick(self, window):
		if window.type == "window":
			if window.isOpen:
				window.par.winclose.pulse()
			else:
				window.par.winopen.pulse()
		return

	def CutFragment(self, string="--8b", leftcut="--", rightcut="b", default=8):
		string = str(string)
		if leftcut in string:
			left = string.find(leftcut) + len(leftcut)
			right = string.find(rightcut)
			output = string[left:right]
			try:
				output = int(output)
			except:
				output = default
		else:
			output = default
		return output

	def Randomize(self, min=0, max=1, seed=absTime.seconds):
		parameter = tdu.remap(tdu.rand(seed), 0, 1, min, max)
		return parameter
