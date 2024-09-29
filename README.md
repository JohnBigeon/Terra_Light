# Terra light

## Concepts 
Remote access to a neopixel strip via micropython and web servers.

## Visuals
The main device looks like:
<div>
  <img src="Screenshots_and_Pictures/integration_v01.bmp" alt="TerraLight." width="800" />
</div>

## Hardware
### Elec design
The schematic and pcb design has been designed via KiCad:
<div>
  <img src="KiCad_files/schematic_terra_light.png" alt="Schematic." width="500" />
  <img src="KiCad_files/pcb_3D.png" alt="PCB." width="500" />
</div>


## Roadmap
This is the expected roadmap for this project:


### Proof of concept: version 0.0.1
- [x] Create webserver via micropython.
- [x] Test the control of leds.
- [x] KiCad design. 


### Audio recognition: version 0.0.2
- [ ] Integrate INMP441 device.
- [ ] Get audio samples
- [ ] Use Tensorflow micropython [https://github.com/mocleiri/tensorflow-micropython-examples/tree/main]
