import asyncio
import sys
import os
import httpx
import traceback

sys.path.insert(0, os.path.dirname(__file__))
from app.config import get_settings
from app.services.llm_service import LLMService

async def main():
    llm = LLMService()
    print("API Key loaded:", bool(llm.api_key))
    
    text = """Page 1: 1 CHAPTER 1 
Microwave Integrated Circuits 
CHAPTER OUTLINE 
1.1 Classification of microw ave integrated circuits 
1.2 Microwave circuits in communication system  1.3 Summary  
1.1 CLASSIFICATION OF MICROWAVE INTEGRATED CIRCUITS  
Active microwave circuit can be defined as a circuit in which active and passive microwave devices 
such as resistors, capacitors, and inductors ar e interconnected by transmission lines. At low 
frequencies, the transmission lines are a simple co nnection; however they are no longer just simple 
connections at microwave frequencies and their o peration becomes a complicated distributed circuit 
element. Subsequently, microwave integrated circuit is classified based on the fabrication method of 
the transmission lines used for interconnection. 
 
 
(a)                                             (b)                                               (c) 
Figure 1.1  Some common transmission lines used in microw ave circuits: (a) coaxial line (b) rectangular 
waveguide, and (c) microstrip line 
 
Page 2: 2   Chapter 1 : Microwave Integrated Circuits 
There are various types of transmission line s in microwave circuits. Common examples of 
transmission lines are waveguides, coaxial, and micros trip lines. Figure 1.1 shows the transmission 
lines used in microwave circuits. Although there are special cases of microwave integrated circuit 
composed of coaxial lines and waveguides, in most cases microwave circuit is integrated using planar transmission lines. Therefor e, the content of this book is restricted to microwave circuits 
integrated using planar transmission lines; examples  of which are microstrip, slot lines, and co-
planar waveguide (CPW), as shown in Fig. 1.2. Such planar transmission lines are frequently 
employed in the large-scale production of microwave circuits and generally forms the basic transmission lines for microwave circuits. The fo llowing text explains how microwave integrated 
circuits are classified with  planar transmission lines.  
  
 
(a)                                                          (b)                                                         (c) 
Figure 1.2  Some common planar transmission lines used in microw ave circuits: (a) microstrip (b) slot line, and 
(c) CPW (CoPlanar Waveguide) 
The implementation of planar transmission lines on substrates can be largely classified into the 
two groups of monolithic and hybrid integrated circuits . In monolithic Integration, active and 
passive devices as well as the pl anar transmission lines are grown in situ  on one planar substrate 
which is usually made from semiconductor material and is called wafer .  
     
  
(a)                                                                             (b) 
Figure 1.3  Monolithic integration: (a) wafer an d (b) the single circuit on wafer1 
 
1 TRW Inc., ALH216C K-Band HEMT Low-Noise Amplifier, 1997 
Page 3: Last Number One Head on Page    3 
Figure 1.3 shows the example of monolithic int egration. Figure 1.3(a) shows a photograph of 
the top side of a wafer and Fig. 1.3(b) showing a si ngle monolithic circuit (the identical circuits are 
repeatedly produced on the wafer in Fig. 1.3(a) ) containing active and passive devices and planar 
transmission lines. An advantage of the monolithic inte gration is that it is well suited for large-scale 
production, which leads to lower cost. The disadvanta ge is that it takes a long time to develop and 
fabricate, and a small-scale production results in highly prohibitive cost. 
Hybrid integration is a fabrication method in which, the transmission lines are implemented by 
conductor patterns on a selected substrate with either printing  or etching ; and active and passive 
devices are assembled on the patterned substrat e by either soldering or wire-bonding. In 
implementing transmission lines by conductor patterns on  substrate, the substrate material as well as 
the conductor material for the transmission lines  needs to be carefully considered because these to a 
large extent affect the characteristics of transmission  lines. Hybrid integration is thus classified into 
three kinds based on the method by which the lines are formed on the substrate; namely printed 
circuit board  (PCB), thick-film  substrate, and thin-film  substrate.  
Figure 1.4 shows an example of how connection lines are formed on a PCB substrate. Both 
sides of the dielectric material are attached with  a copper clad which is then etched to obtain the 
desired patterns. For PCB substrate materials, epoxy-fiber-glass  (FR4), teflon , and duroid  are 
widely used. FR4 substrate (that is a kind of epoxy-fiber-glass) can be used from lower frequencies 
to approximately 4 GHz, while the others such as tefl on or duroid can be used up to the millimeter 
wave region, depending on their formation. Gene rally, all these materials lend themselves to 
soldering while wire-bonding as an integrated circuit assembly is typically, not widely used. Furthermore, compared with other methods which will  be explained later, PCB can provide a lower 
cost; its fabrication is easy and t akes a shorter time to produce. In  addition, production on a small-
scale is possible without the use of expensive assembly  machines; it is easy to fix and could also be 
used on a large-scale production; and is thus widely used.   
 
 
Figure 1.4  A photograph of PCBs  
Thick films substrate are produced by screen printing techniques; in which conductor and 
dielectric patterns are printed using screen on ceramic substrates. The reason for naming it thick film is that, the patterns formed by such techni que are generally much thicker than that formed 
using thin film techniques. As a benefit of using printing techniques, multiple printing is possible. 
Through the printing of dielectric ma terials, it is also possible to form capacitors. Due to the use of 
ceramic substrate which is more tolerant to heat, it is easy to assemble active devices in the form of 
Page 4: 4   Chapter 1 : Microwave Integrated Circuits 
chips. On the other hand, considering lines and pat terns formed by this process, the pattern accuracy 
of thick film is inferior to some extent compared to thin film. The cost and development time, on case by case basis, could be seen to lie between those of PCB and thin film process. Figure 1.5 shows a photograph of an IC fabricated and assembled using thick film process. 
 
Figure 1.5  A photograph of substrates fa bricated by thick film process 
Thick film technique is very widely used in the f abrication of microwave circuits for military and 
microwave communication systems. In the case of t he thin film process, a similar ceramic substrate 
material used as in thick film is employed, but compared to thick film substrate; a fine surface-
finish substrate is used. The most wi dely used substrate is 99% alumina (Al 2O3). The pattern 
formation on the substrate is by photolithog raphic process, which can produce fine tracks of 
conductor patterns close to those in semiconductor process. As in the case of thick film, it is 
possible to assemble directly semiconductor chips and wire-bonding is primarily used in the assembly. Thin film compared to PCB and thick film, is more expensive, and due to the requirement of fine tracks, a mask fabrication is accompanied and the process generally takes a longer time. Passive components such as resistors and air-bridge ca pacitors are also possible with this process. 
Furthermore, integrated circuits produced by thin film require special wire bonders and micro-welding equipment for assembly. Compared to monolithic integration process, it tends to be cheaper in terms of the cost; however the thin film process tends to have large unknown and not precisely described parasitic circuit elements accompanied due to assembly such as wire bonding. Figure 1.6 is a photograph of thin film circuits fabricated by thin film technique. 
 
Figure 1.6  A photograph of substrates produced by thin film process 
Page 5: Last Number One Head on Page    5 
The choice of integration method depends on t he application and situation, taking into account 
several factors that were mentioned before. For in stance, factors such as, the operating frequency of 
integrated circuit, the forms of semiconductor components (chip or packaged), the forms of the 
passive components, large-scale fabrication costs, and method of assembly should all be considered 
in selecting the optimum method of integration. 
1.2 MICROWAVE CIRCUITS IN COMMUNICATION SYSTEM  
Integrated circuit classification has been discussed previously. Integrated circuit was found to be classified based on the method of implementing t he planar transmission lines, for the purpose of 
connecting active and passive devices. The functions of  integrated circuits vary greatly and the next 
matter has to do with which circuit designs are re ferred to. Examples of such circuits are low noise 
amplifier (LNA), power amplifier (PA), oscillator,  mixer, directional coupler, switch, attenuator, 
filter and a host of other microwave integrated circ uits. Among these, directional coupler, switches, 
attenuators, filters, etc are basically passive micr owave circuits although they are very widely used. 
Thus, they are not covered in this book because they are considered to be outside the scope of the book. Furthermore, although components such as sw itches, variable attenuators, phase shifters and 
other control circuits are important and composed of semiconductor devices, they are generally not 
regarded as the basic building blocks  of a wireless system. This book will therefore cover the basic 
design theory as well as devices related to these circuits such as amplifiers, oscillators and mixers, which are the most frequently used circuits to build wireless communication systems.  
 
 
Figure 1.7  A block diagram of an analog mobile phone handset 
 
Page 6: 6   Chapter 1 : Microwave Integrated Circuits 
Figure 1.7 is a block diagram of an analog cellular phone handset. This block diagram 
represents also a general transceiver for the tran smission and reception of analog signal (usually 
voice). Weak RF signals received from the antenna first go through a filter called a diplexer and the signal in the receiver frequency band  is filtered. The filtered signal is too weak for demodulation or 
signal processing, and an amplifier called low nois e amplifier is required to amplify the signal. 
Next, because the signal frequency is so high, the mixer shown in Fig. 1.7 translates the carrier 
frequency to a lower frequency band called IF (Int ermediate Frequency). Multiples of other signals 
generally coexist with the signal in the IF. In order to select the desired signal (usually called the channel) from the multiples of other signals or to filt er out possible spurious signals that presents at 
the mixer output, the signal is passed through a narrow band bass filter that has a bandwidth of about the signal bandwidth. Note that the mixer requires the input signal from a local oscillator  
(LO)  for the translation of the signal frequency to the IF. The LO frequency is generally synthesized 
using phase locked loop  (PLL). The IF signal is then passed through a demodulator for the recovery 
of the original signal. 
In the transmission operation, the input signal  goes to the modulation input of transmitting 
VCO, and the signal is modulated to have the desired carrier center freq uency that is similarly 
synthesized by PLL technique, which results in frequency modulated (FM) signal. The modulated 
signal is then pass through the band pass filter to filter out unnecessary spurious. The average 
output power level of the modulated signal is generally low; thus in order to obtain the desired RF 
power output level, the signal needs to be amplifi ed by a power amplifier (PA). The signal is then 
passed through a diplexer, without affecting the receiver, and radiated via the antenna. 
It could thus be inferred that, the key circuits in building a communication system are low noise 
amplifier, power amplifier, oscillators and mixers. Therefore, this book will address the design and 
evaluation method of these circuits and the de tailed discussion of these will be covered. 
1.3 SUMMARY  
Among active microwave circuits, the most commonl y used are amplifiers, oscillators, and mixers, 
and their fabrication can be classified into monolithic  and hybrid integration. In hybrid integration, 
the lines used for interconnection is implemented on  a separate substrate, and on this, active and 
passive devices are assembled. Based on the fabricat ion method of the substrate, hybrid integration 
can be further classified into integrations based on P CB, thick film, and thin film. In the selection of 
integration, one cannot be said to be superior to the other; the choice is made depending on the application and given situation, and taking in to consideration several other factors.  
REFERENCES  
[1] G. Gonzalez, Microwave transistor amplifiers analysis and design , 2nd edition, Prentice Hall, 
1997. 
[2] T. S. Lavergetta, Microwave materials and fabrication techniques , Artech House, 1984. 
Page 7: Last Number One Head on Page    7 
[3] K. C. Gupta, Microstrip lines and slot lines , 2nd edition Artech House 1996. 
   
 
       
 
Microwave Circuits  ..................................................................................................................... 5 
local oscillator (LO)  ............................................................................................................ 6 
low noise amplifier (LNA)  .................................................................................................. 5 
phased locked loop (PLL)  ................................................................................................... 6 
powere amplifier (PA)  ......................................................................................................... 5 
Microwave Integrated Circuits  .................................................................................................... 1 
co-planar waveguide(CPW)  .......................................................................................... 1 
hybrid integration  ................................................................................................................ 3 
printed circuit board(PCB)  .......................................................................................... 3 
substrate  ....................................................................................................................... 3 
thick-film  ..................................................................................................................... 3 
thin-film  ....................................................................................................................... 3 
microstrip .................................................................................................................... ........ 1 
monolithic integration  ......................................................................................................... 2 
slot line  .............................................................................................................................. .. 1 
"""

    print("Calling generate_lecture on LLMService...")
    try:
        res = await llm.generate_lecture(text, mode="discussion")
        if res:
            print("Response obtained successfully!")
            print(res[:200])
        else:
            print("Returned None!")
    except Exception as e:
        print("Exception caught in test:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
