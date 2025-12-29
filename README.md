REMOTE CONTROL
------------------------------------------------------
It is a nine key, one encoder remote controller for multiple things (in my case it is used for a survailance robot). It has nine keys in 3X3 pattern, each key have its own function placed as follows, the speed control can be done by rotatory encoder.
<img width="552" height="362" alt="image" src="https://github.com/user-attachments/assets/5dd88ff8-5941-4f5b-a388-f72e86e2f5de" />

-----------------------------------------------------
PCB
-----------------------------------------------------
Here is my schematic PCB, i am using this design on the board;

<img width="745" height="428" alt="image" src="https://github.com/user-attachments/assets/03fd6815-d0a1-4d94-99ca-2293c9b26eba" />

picture of PCB editor,

<img width="843" height="534" alt="image" src="https://github.com/user-attachments/assets/17d35721-49af-4018-be80-13bc708230ed" />

I used Ki-cad to make pcb from start.
-----------------------------------------------------
CAD
-----------------------------------------------------
It is a basic box with soft cornor, and some decorations. Contains of Two 3D printed parts, top cover and bottom case.
Pinned with four screw, have a PCB in middle.

<img width="775" height="504" alt="image" src="https://github.com/user-attachments/assets/1a796272-2a1b-4e3c-86cd-5e83f5845ae8" />

I used Fusion 360! to design the case.
------------------------------------------------------
Firmware overview
------------------------------------------------------
This is code of KMK firmware.
The keys send direction and mode commands, the rotary encoder controls robot speed, and the OLED shows the current mode and last action.
Everything works together like a compact robot remote controller with visual feedback.
-----------------------------------------------------
Challanges
-----------------------------------------------------
This is my first hackpad, I never made any PCB, nor a 3D case (or any 3D object using Fusion 360). I had to learn every thing from scrach used multiple tutorials, AI and google docs for documentation.
With my online classes it took more than a week to learn everything and every important tools.
-----------------------------------------------------
BOM
-----------------------------------------------------
Here is everything, you need to set this PCB:-
XIAO RP2040------1
MX Switches------9
1N4148 Diodes----9
EC11 Encoder-----1
0.91″ OLED-------1
Keycaps----------9
