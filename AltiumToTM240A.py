import json

# prompt user for details of new feeder
def newFeeder(feederName):
    feederData = ['empty']*6
    print("Enter stack number for", key, "feeder:")
    inputString = input()
    feederData[0] = inputString

    print("Enter x offset in mm for", key, "feeder (default: 0):")
    inputString = input()
    if (not(inputString == '')):
        feederData[1] = inputString
    else:
        feederData[1] = '0';
    
    print("Enter y offset in mm for", key, "feeder (default: 0):")
    inputString = input()
    if (not(inputString == '')):
        feederData[2] = inputString
    else:
        feederData[2] = '0';
    
    print("Enter rotation offset for", key, "feeder (default: 90):")
    inputString = input()
    if (not(inputString == '')):
        feederData[3] = inputString
    else:
        feederData[3] = '90';
    
    print("Enter feed rate in mm for", key, "feeder (default: 4):")
    inputString = input()
    if (not(inputString == '')):
        feederData[4] = inputString
    else:
        feederData[4] = '4';
    
    print("Enter nozzle for", key, "feeder (options: 1 or 2, default: 1):")
    inputString = input()
    if (not(inputString == '')):
        feederData[5] = inputString
    else:
        feederData[5] = '1';
        
    return feederData


print('Enter your input file (Either full path or name of file in working directory, include file extension):')
inputFilename = input()

print('Enter production layer (Check your csv for the layer name, default: TopLayer):')
productionLayer = input()
if productionLayer == '':
    productionLayer = 'TopLayer'

originOffset = [0]*2
# Get origin offset from user
print("Enter required x-axis origin offset in mm (default: 0):")
inputString = input()
if (not(inputString == '')):
    originOffset[0] = inputString
else:
    originOffset[0] = '0';
        
print("Enter required y-axis origin offset in mm (default: 0):")
inputString = input()
if (not(inputString == '')):
    originOffset[1] = inputString
else:
    originOffset[1] = '0';
    
    

componentTypes =[]

# Analyze component types/feeder requirements
print('\nScanning Input File . . .')
with open(inputFilename, 'r') as infile:
    
    # find where data starts. Could probably use a fixed offset if this turns out to be unreliable
    for line in infile:
        row = line.strip().split(',')
        if row[0] == '"Designator"':
            break
    
    for line in infile:
        row = line.strip().split(',')
        # skip any components not for the production layer
        if not(row[2].strip('"') == productionLayer):
            print('skipped non-production-layer component', row[0])
            continue
        
        # get component info
        row = line.strip().split(',')
        componentTypes.append(row[1].strip('"'))

components = dict.fromkeys(componentTypes)  # dictionary with one key for each component type


inputString = ''
      
# load feeder config
try:
    feedersFile = open('feeders.json', 'r')
except:
    print('No feeder config file found (feeders.json)')
    feeders = dict
else:
    print('Loaded feeder config.')
    try: 
        feeders = json.load(feedersFile)
    except:
        print('Error loading feeder config, feeders.csv may be empty')
        feeders = {}
    else:
        # show user currently loaded feeders
        print("Current Feeders:\n{:<20} {:<5}".format('Name','Stack Number'))
        for feeder in feeders:
            print("{:<20} {:<5}".format(feeder, feeders[feeder][0]))
        del feeder
        print('\n')


# Attempt to match components to feeders
for key in components:
    try:
        components[key] = feeders[key]
    except:
        print('\n'+key+' not matched to an existing feeder')
    
        # ask if user wants to make a new feeder
        print('Add new feeder, match to feeder manually, or skip? (new, match, skip; default: skip)')
        inputString = input()
        if inputString == 'new' or inputString == 'n':
            feeders[key] = newFeeder(key)                    # add feeder
            components[key] = feeders[key]                   # associate new feeder with component
        elif inputString == 'match' or inputString == 'm':
            # show user currently loaded feeders
            print("Current Feeders:\n{:<20} {:<5}".format('Name','Stack Number'))
            for feeder in feeders:
                print("{:<20} {:<5}".format(feeder, feeders[feeder][0]))
            del feeder
            print('\nEnter name of feeder to match with '+key+':')
            components[key] = feeders[input()]
            
        else:
            print(key+' components will not be populated\n')
    else:
        print(key+' successfully matched to an existing feeder')


# save modified feeder data
with open('feeders.json', 'w') as feedersFile:
    json.dump(feeders, feedersFile)

# generate output file
print('\nGenerating Output File . . .')
with open(inputFilename, 'r') as infile:
    with open('output.csv', 'w') as outfile:    
        
        # Generate origin offset section
        outfile.write('%,OriginOffset,X,Y\n')
        outfile.write('65535,0,'+originOffset[0]+','+originOffset[1]+'\n')
        
        # Generate stack offset section
        outfile.write('%,StackOffset,StackNo.,X,Y\n')
        for key in components:
            # skip any components without a feeder
            if not(components[key]):
                continue
            outfile.write('65535,'+'1,'+components[key][0]+','+components[key][1]+','+components[key][2]+'\n')
                
        # Generate feedrate section
        outfile.write('%,FeedSet,StackNo.,Rate\n')
        for key in components:
            # skip any components without a feeder
            if not(components[key]):
                continue
            outfile.write('65535,'+'2,'+components[key][0]+','+components[key][4]+','+'\n')
        
        # TODO:Generate Image Section       
        
        
        # Generate Components Section
        outfile.write('%,NozzleNo.,StackNo.,X,Y,Angle,Depth,Skip,Comment\n')
        index = 1
        outrow = [0] * 9;
        # find where data starts in input file
        for line in infile:
            row = line.strip().split(',')
            if row[0] == '"Designator"':
                break
    
    
        for line in infile:
            row = line.strip().split(',')
            
            # skip any components not for the production layer
            if not(row[2].strip('"') == productionLayer):
                print("Skipped {:<8} Non-production-layer component".format(row[0].strip('"')))
                continue
            
            # skip any components without a feeder
            elif not(components[row[1].strip('"')]):
                print("Skipped {:<8} No Feeder".format(row[0].strip('"')))
                continue
            
            # component placements
            outrow[0] = str(index)                                                   #component number
            outrow[1] = components[row[1].strip('"')][5]                             #nozzle
            outrow[2] = components[row[1].strip('"')][0]                             #stack #
            outrow[3] = str(round(float(row[4].strip('"')), 2))                      #x
            outrow[4] = str(round(float(row[5].strip('"')), 2))                      #y 
            rotation = round(int(row[6].strip('"')) + int(components[row[1].strip('"')][3]), 0)
            if rotation > 180:
                rotation = rotation - 360       # need to convert from 0 - 360 to -180 - +180
            outrow[5] = str(rotation)                                                #rotation 
            outrow[6] = str(round(float(row[7].strip('"')), 2))                      #depth
            outrow[7] = '0'                                                          #skip
            outrow[8] = row[0].strip('"')                                            #comment/designator
            
            outfile.write(','.join(outrow) + '\n')
            index = index + 1
print('Output file successfully generated.\n')