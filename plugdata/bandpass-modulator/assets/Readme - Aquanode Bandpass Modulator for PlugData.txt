Aquanode Bandpass Modulator for PlugData (https://plugdata.org/)
 aquanode.gumroad.com | aquanode.bandcamp.com | www.youtube.com/@aquanodemusic

Hi! Thank you for downloading my PlugData Bandpass Modulator Patch.

What is it:
It's a bandpass filter whose frequency and panning can be randomized in two ways.
First, the frequency peak of the bandpass filter can be automated to randomly jump around.
But there's also a skew option working simultaneously to modulate the already randomly jumping peak's position even more.
The combined effect is that it slews around all over the place in jumps with semi-smooth behaviour from the skewing inbetween.
Thus it performs great for effects from Filter FM-like sounds to bubbly effects to slow and mellow panning and delay.
Is it special? Maybe, maybe not — you can definitely build something like this in your DAW on your own. 
But setting up all those randomizations takes a long time.
I'm speaking from experience here since this PlugData patch is a recreation of something I previously built in FL Studio using the Patcher environment!
The visuals in FL Studio are nicer, but PlugData is completely free, open-source, and works in many operating systems and probably ALL DAWs that support VST plugins.

Changelog: 
This plugin comes in three versions, a 
- alpha version (v0), 
- beta version (v1) with state recalls enabled, and
- complete version (v2) where the type of the skewing can be chosen as well.
Versions v1 and v2 will remember your settings and also exposes all the knobs to your DAWs automization capabilities. For these, reloading the plugin does not reset all values to default ones anymore as in the alpha version.

How to use:
Download PlugData as a VST. Then, use its FX version, add it on the mixer track where your synth or audio source is routed to, and open my preset in the VST.
If you see all the cables of the patch, press the plug symbol on the top right corner to go into plugin mode.
Each knob comes with its own display showing the current value it has.
If you want to edit the ranges of the knobs, click on the pencil icon if you are in plugin mode to get into the edit mode of plugdata. 
Then, you can click on each knob and on the right hand side there is a menu where you can edit the ranges of the knobs.

Note: 
Apparently state changes are not always saved when in Plugin Mode. You can also instead choose
presentation mode, which is the third symbol in the top middle view mode selection group, which might work better.

Controls overview:
Randomization and Modulation
- Activate Frequency Randomization: Enables random jumping of the filter frequency within the specified range.
- Activate Panning Randomization: Enables random stereo panning of the filter signal.
Volume & Filter Controls
- Smoothe (samples): Applies smoothing to transitions. Set it low to avoid audio clicks, or zero if you want clicky jumps.
- Original Vol (0–1): Sets the dry signal level before filtering.
- Filter Vol (0–20): Controls the amplitude of the filtered (wet) signal. It goes up to 20 (2000%) since the filter can be quiet.
- Filter Q: Changes resonance of the bandpass filter — higher values create a narrower, sharper and louder peak.
Filter Frequency Range
- Filter Frequency Range From (Hz) and To (Hz): Sets the range used for frequency randomization. The bandpass peak will then only jump around in that bandwidth.
- Speed (ms): Determines how fast the frequency and/or panning values are updated.
Stereo and Skew Controls
- Pan Offset: Adds a constant offset to the random panning values from the frequency randomization.
- Skew Vol: Adds a sine-based modulation layer to the random frequency changes. Its amplitude corresponds to the frequency range (From Hz and To Hz) you've set.
- Skew Freq: Controls how fast the skew modulation cycles through (i.e., the LFO frequency).
- Skew Type: Changes the basic shape of the skew modulator.
Delay Section
- Activate Delay: Enables a simple delay on the filter signal.
- Delay Time (ms): Time before the delayed signal is played back.
- Decay: Decay factor of the delay. If for example it has the value 0.9, then the next delay trigger is 90% as loud as the previous one.
Visual Feedback
- Bandpass State Display: Shows a live visualization of the filter frequency over time.
- Filter Frequency (Hz): A slider showing the current frequency. This value changes in real time and corresponds to the bandpass position seen in the state waveform.
- Filter Panning (-1 to +1): Shows the current position of the filter in the stereo field.

Note:
Filter Frequency, Delay, and Panning state recall is disabled — they will be turned on and randomize on each load until you turn off the randomization options.

Credits:
Of course the makers of Pure Data and Plug Data to make this patch possible.
Ewan Bristow's EB-Morph pure data patch which I dissected to understand how to make the DAW state saving work and the knob values recallable.
And finally to myself, or rather my earlier Bandpass Modulator I made in FL Studio.
I have added the FL Studio version in this download package here too, feel free to play around with it as well if you have FL Studio.

Thanks again and have fun playing around with it!
- Aquanode

-----------------------------------------------------------------

BELOW IS THE DESCRIPTION FOR MY FL STUDIO PRESET, IF YOU ONLY WANT TO USE THE PLUGDATA VERSION FEEL FREE TO IGNORE THIS
AutoMorph BandpassMod EQ
Automated EQ Bandpass Modulator Preset for FL Studio 
by Aquanode (aquanode.bandcamp.com / aquanode.gumroad.com)

AutoMorph BandpassMod EQ is a Bandpass Modulation Effect for evolving pads inspired by the
Random and Modulation Filters from the Korg Triton Workstation Synthesizer.

What it does:
It uses a Bandpass Filter from an EQ and modulates its spectral / frequency position. It can either 
jump to a different frequency band directly after a short pause, move to it quickly or a combination of both,
i.e. it moves a bit and then jumps (which can be controlled in the "skew" section of my plugin).

How to use:
Drag and Drop the .fst file into a mixer track and it opens and affects the sound automatically.
Alternatively, open the preset directory of FL Studio and paste the file there, it will then
automatically appear under your installed Effects.

Description of the parameters:
Vol Dry: 			How much unaltered signal should be audible.
Vol Wet: 			How much altered signal should be audible.
Bandpass Settings - Low Limit: 	Lower Limit of possible frequency positions. The bandpass peak cannot fall below the set value.
Bandpass Settings - High Limit:	Higher frequency limit. If it is set to a smaller value than the lower limit, their roles swap.
Bandpass Settings - Fine:	Fine Control, shrinks the frequency jumping interval on both ends and keeps a smaller interval in the middle. 
				Example: If Low Limit = 1000 Hz, High Limit 2000 Hz and Fine = 50% then it can only jump from 1250 to 1750 Hz.
Bandpass Settings - Speed:	How much time it takes until the bandpass jumps to another (random) value.
Bandpass Settings - Mod Type:	Default is Random Jumps at 100% knob value, can also be sine curves or similar.
Bandpass Settings - Bandwidth:	The frequency width of the bandpass filter.
Bandpass Settings - Strength:	The strength of the bandpass filter (does not affect the sound very much).
FX - Dist:			Distortion to the bandpassed signal.
FX - Delay Speed:		Changes the speed of the Delay (if activated).
FX - Delay Vol:			Activates a Delay if >0% and sets its volume.
FX - Reverb:			Adds Reverb after the Delayed Signal.
Modulation - Autopan:		Sets if the bandpassed signal should be panned in the stereo field randomly and to what strength.
Modulation - Skew Type:		Sets the type of the modulation, it basically adds another Bandpass Modulation on top to get more interesting 
				behaviour. For example: If the Bandpass is moving as a sine wave through the frequency spectrum, you can add
				another quieter sine wave at a higher frequency with the skewness knobs, that gets added to the original one.
Modulation - Skew Speed:	Sets how fast the bandpass frequency gets skewed between jumps.
Modulation - Skew Amt:		Sets if the bandpass should move / be skewed between jumps and how much (if >0). This smoothes the Bandpass jumps
				and sounds somewhat smooth. You can almost get "water bubble" sound effects from this.

I hope it is useful, thanks for trying it out!