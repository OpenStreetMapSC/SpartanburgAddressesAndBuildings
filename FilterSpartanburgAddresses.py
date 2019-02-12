'''
A translation function for Spartanburg county shp address data (structurepoints.*). 


The following fields are used:    

Field           Used For            Reason

addr:street taken from -
FULLNAME        addr:street                If STREETNAME + TYPE + PREDIR do not work
PREDIR          Road direction prefix
TYPE            Road type (street, ave, etc)
STREETNAME      Base road name

AUNUMBER        addr:unit
COMMUNITY       addr:city
STADD           addr:housenumber
ZIP             addr:postcode


Fixed field:
                addr:state=SC

'''

import re

def translateName(rawname,warn):
    '''
    A general purpose name expander.
    '''
    suffixlookup = {
    'Aly':'Alley',
    'Anx':'Annex',
    'Ave':'Avenue',
    'Av':'Avenue',
    'Br':'Branch',
    'Blf':'Bluff',
    'Byp':'Bypass',
    'Rd':'Road',
    'Hts':'Heights',
    'St':'Street',
    'Pl':'Place',
    'Hl':'Hill',
    'Holw':'Hollow',
    'Pk':'Park',
    'Cres':'Crescent',
    'Blvd':'Boulevard',
    'Dr':'Drive',
    'Dwns':'Downs',
    'Ext':'Extension',
    'Ext.':'Extension',
    'Pkwy':'Parkway',
    'Pky':'Parkway',
    'Lndg':'Landing',
    'Xing':'Crossing',
    'Lane':'Lane',
    'Cv':'Cove',
    'Crt':'Court',
    'Trl':'Trail',
    'Tr':'Trail',
    'Ter':'Terrace',
    'Terr':'Terrace',
    'Trac':'Trace',
    'Trc':'Trace',
    'Trce':'Trace',
    'Vly':'Valley',
    'Xovr':'Crossover',
    'Gr':'Grove',
    'Grv':'Grove',
    'Ln':'Lane',
    'Lk':'Lake',
    'Cl':'Close',
    'Cv':'Cove',
    'Cir':'Circle',
    'Ct':'Court',
    'Est':'Estate',
    'Rl':'Real',
    'Rdg':'Ridge',
    'Plz':'Plaza',
    'Pne':'Pine',
    'Pte':'Pointe',
    'Pnes':'Pines',
    'Pt':'Point',
    'Ctr':'Center',
    'Rwy':'Railway',
    'Div':'Diversion',
    'Mnr':'Manor',
    'Hwy':'Highway',
    'Hwy':'Highway',
    'Conn': 'Connector',
    'Chase': 'Chase',
    'Vw': 'View',
    'View': 'View',
    'Cliff': 'Cliff',
    'Walk': 'Walk',
    'Knob': 'Knob',
    'Gate': 'Gate',
    'Grove': 'Grove',
    'Path': 'Path',
    'Trail': 'Trail',
    'Place': 'Place',
    'Real': 'Realignment',
    'Pass': 'Pass',
    'Row': 'Row',
    'Way': 'Way',
    'Farm': 'Farm',
    'Run': 'Run',
    'Drive': 'Drive',
    'Loop': 'Loop',
    'Line': 'Line',
    'E':'East',
    'S':'South',
    'N':'North',
    'W':'West'}
	
    newName = ''
    for partName in rawname.split():
        trns = suffixlookup.get(partName,partName)
        if (trns == partName):
            if partName not in suffixlookup:
                if warn:
                    print ('Unknown suffix translation - ', partName)
        newName = newName + ' ' + trns

    return newName.strip()


# Only apply translation to first and last word
def translateFullName(rawname):
    newName = ''
    nameParts = rawname.split()
    for idx, partName in enumerate(nameParts):
        if idx == 0:
            partName = translatePrefix(partName)
        elif idx == (len(nameParts)-1):
            partName = translateName(partName,True)
        newName = newName + ' ' + partName

    return newName.strip()


def translatePrefix(rawname):
    '''
    Directional name expander.
    '''
    prefixLookup = {
        'O':'Old',
        'N':'New',
        'NW':'NorthWest',
        'NE':'NorthEast',
        'SE':'SouthEast',
        'SW':'SouthWest',
        'E':'East',
        'S':'South',
        'N':'North',
        'W':'West'}

    newName = ''
    for partName in rawname.split():
        newName = newName + ' ' + prefixLookup.get(partName,partName)

    return newName.strip()


# Convert from 22Nd to 22nd
def CorrectNumberedCapitalization(rawname):
    newName = ''
    for partName in rawname.split():
        word = partName
        if (word[0].isdigit()):
            word = word.lower()
        newName = newName + ' ' + word

    return newName.strip()

#see if type was apecified in both base STREETNAME and on type
#For example Oak Street Street
def CheckDoubleType(rawName):
    newName = rawName
    nameParts = rawName.split()
    numberOfParts = len(nameParts)
    if numberOfParts >= 3:
        testSuffix = translateName(nameParts[numberOfParts-2],False)
        lastWord = nameParts[numberOfParts-1]
        if (lastWord == testSuffix):
            del nameParts[-1]  # remove last element
            nameParts[numberOfParts-2] = testSuffix # replace last word with expanded word
            newName = ' '.join(nameParts)

    return newName.strip()


    
def filterTags(attrs):
    if not attrs:
        return

    tags = {}
    
    if 'STADD' in attrs:
        housenumber  = attrs['STADD'].strip()
        if housenumber == '0':
            return  tags # Placeholder address?
        if housenumber != "":
            tags['addr:housenumber'] = housenumber

    roadName =''
        
    if 'PREDIR' in attrs:
        translated = translatePrefix(attrs['PREDIR'])
        roadName = roadName + translated
        #if translated != '(Lane)' and translated != '(Ramp)':
        #    tags['name'] = translated

    if 'STREETNAME' in attrs:
        roadName = roadName + ' ' + attrs['STREETNAME'].title().strip()

    if 'TYPE' in attrs:
        translated = translateName(attrs['TYPE'].title(),True)
        roadName = roadName + ' ' + translated

    roadName = roadName.strip()
    if roadName=='':
        # couldn't build road name from parts, try full name
        if 'FULLNAME' in attrs:
            roadName = translateFullName(attrs['FULLNAME'].title())

    roadName = roadName.strip();
    roadName = CorrectNumberedCapitalization(roadName)
    roadName = re.sub("\s\s+", " ", roadName)  # Remove multiple spaces
    roadName = CheckDoubleType(roadName)
    if roadName != '':
        tags['addr:street'] = roadName
        
        
    if 'COMMUNITY' in attrs:
        city  = attrs['COMMUNITY'].strip().title()
        if city != '':
            tags['addr:city'] = city
        
    if 'AUNUMBER' in attrs:
        unit  = attrs['AUNUMBER'].strip()
        unit = re.sub("\s\s+", " ", unit)  # Remove multiple spaces
        if unit != "":
            tags['addr:unit'] = unit

    if 'ZIP' in attrs:
        zip = attrs['ZIP'].strip()
        if zip != '':
            tags['addr:postcode'] = zip

    tags['addr:state'] = 'SC'

    return tags