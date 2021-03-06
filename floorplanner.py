import re
import math 
import sys, os
#remember  route_padnets_outside


aspect_ratio = raw_input('aspect ratio: ')
utilization = raw_input('utilization: ')
cells_area = raw_input('cells_area: ')
#height = raw_input('height: ')
#width = raw_input('width: ')
celfile = raw_input('Graywolf .cel file name: ')
splitName = celfile.split(".")
designName = splitName[0]

total_core_area = float(cells_area)/float(utilization)
w= int((float(total_core_area)/float(aspect_ratio))**(0.5))
h = int(total_core_area/w)
x_min = 0
y_min = 0
x_max = x_min + w
y_max = y_min + h

parFile = designName + ".par"
f= open(parFile,"w+")
#to be inserted in beginning of file
f.write("RULES\n# values are resistance in ohms/sq and capacitance in fF/um^2\nlayer metal1 0.07 0.030 horizontal\nlayer metal2 0.07 0.017 vertical\nlayer metal3 0.07 0.006 horizontal\nlayer metal4 0.04 0.004 vertical\n\nvia via12 metal1 metal2\nvia via23 metal2 metal3\nvia via34 metal3 metal4\nwidth metal1 60\nwidth metal2 60\nwidth metal3 60\nwidth metal4 120\nwidth via12 60\nwidth via23 60\nwidth via34 120\n\n# Set spacing = track pitch - width, so that GrayWolf places pins\n# on the right pitch.\n# Pitches are (in um):\n# metal1 = 200,  metal2 = 160,  metal3 = 200,  metal4 = 320\n\nspacing metal1 metal1 140\nspacing metal2 metal2 100\nspacing metal3 metal3 140\nspacing metal4 metal4 200\n\n# Stacked vias allowed\nspacing via12 via23 0\nspacing via23 via34 0\n\noverhang via12 metal1 8\noverhang via12 metal2 6\n\noverhang via23 metal2 8\noverhang via23 metal3 6\n\noverhang via34 metal3 14\noverhang via34 metal4 16\nENDRULES\n\n*vertical_wire_weight : 1.0\n*vertical_path_weight : 1.0\n*padspacing           : variable\n*rowSep		      : 0.0   0\n*track.pitch	      : 160\n*graphics.wait        : off\n*last_chance.wait     : off\n*random.seed	      : 12345\n")

AR_string = "TWMC*chip.aspect.ratio : " + aspect_ratio + "\n"
f.write(AR_string)
coreArea_string = "TWMC*core: " + str(x_min) + " " + str(y_min) + " " + str(x_max) + " " + str(y_max) + "\n"
f.write(coreArea_string)

#to be inserted at the end of the file
f.write("TWSC*feedThruWidth    : 160 layer 1\nTWSC*do.global.route  : on\nTWSC*ignore_feeds     : true\nTWSC*call_row_evener	: true\nTWSC*even_rows_maximally : true\n# TWSC*no.graphics    : on\n\nGENR*row_to_tile_spacing: 1\n# GENR*numrows		: 6\nGENR*flip_alternate_rows : 1")
f.close()

pinPlaceFlag = raw_input('Specify Pin Placement? (Y/N): ')

if pinPlaceFlag == "Y":
  pinplacement = raw_input('Pin placement file:')


  #open .cel file to add pads in it, for every pin name given in the pins placement, look for its pad name in the .cel
  #read pins placement
  with open(pinplacement) as f2:
      content = f2.readlines()
  with open(celfile) as f3:
      cel = f3.readlines()

  for line in range(len(cel)):
      if cel[line].startswith("restrict"):
         del cel[line]
      if cel[line].startswith("padgroup"):
         del cel[line:len(cel)]
         break

  permute=""
  padplace=""
  padGroups=0
  padsInGroup=[]
  for x in content:
      x = x.strip()
      if x.startswith("{"):
          padGroups = padGroups + 1
          x = re.sub('[{}]', '', x)
    	  a = x.split(":")
       	  pins = a[0].split(",")
       	  c = "nopermute"       	
          c = a[1].split(",")
       	  padplace = "restrict side " + c[0] + "\n"
          padname = ""
       	  permute = c[1]
       	  for pin in pins:
            pinPattern = "^pin .* " + pin + "(^|\s)*" + "signal"
            regex = re.compile(pinPattern)
       	    #look in .cel for pin name and find its pad
            for i in range(len(cel)):
             if regex.search(cel[i]):
                if(cel[i-1].startswith("pad")):
                   reqString = cel[i-1].strip()
                   padline = reqString.split(" ")
                   padname = padline[-1]
                   padsInGroup.append(padname)
                elif(cel[i-2].startswith("pad")):
                   reqString = cel[i-2].strip()
                   padline = reqString.split(" ")
                   padname = padline[-1]
                   padsInGroup.append(padname)
                elif(cel[i-3].startswith("pad")):
                   reqString = cel[i-3].strip()
                   padline = reqString.split(" ")
                   padname = padline[-1]
                   padsInGroup.append(padname)
                elif(cel[i-4].startswith("pad")):
                   reqString = cel[i-4].strip()
                   padline = reqString.split(" ")
                   padname = padline[-1]
                   padsInGroup.append(padname.strip())
                break
       	  #create pad group
          padGroup = "padgroup " + str(padGroups) + " " + permute + "\n"
       
          for j in padsInGroup:
                padGroup = padGroup + j + " nonfixed\n"
          padGroup = padGroup + padplace
          cel.append(padGroup)
          padGroup = ""
          padsInGroup = []
        
      else:
         a = x.split(":")
         #add this line after pad definition:
         pinPattern = "^pin .* " + a[0] + "(^|\s)*" + "signal"
         regex = re.compile(pinPattern)
         padplace = "restrict side " + a[1] + "\n"
         for i in range(len(cel)):
             if regex.search(cel[i]):
                if(cel[i-1].startswith("restrict")):
                   cel[i-1] = padplace
                elif(cel[i-2].startswith("restrict")):
                   cel[i-2] = padplace
                else:
                   cel.insert(i, padplace)
  f3=open(celfile,"w")
  for item in cel:
      f3.write("%s" % item)
  f2.close()
  f3.close()

runString = "graywolf " + designName 
os.system(runString)              
