import os, os.path, sys, getopt, re, json
from os import path

def main(argv):
    inputfile = ''
    outputdir = ''
    json = False

    try:
        opts, args = getopt.getopt(argv,"hi:o:j",["ifile=","ofile=","json"])
    except getopt.GetoptError:
        print('usage: beholder.py -i <input_file> -o <output_directory>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('usage: beholder.py -i <input_GNMAP_file> -o <output_directory>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            if path.exists(arg):
                if arg.endswith('.gnmap'):
                    inputfile = arg
                else:
                    print('Error: Incorrect file type\nPlease provide a .gnmap file')
                    sys.exit(2)
            else: 
                print(f'Error: {arg} does not exist')
                sys.exit(2)
        elif opt in ("-o", "--ofile"):
            if path.isdir(arg):
                outputdir = arg
            else: 
                print(f'Error: No such directory\n{arg} does not exist')

        elif opt in ("-j", "--json"):
            json = True

    parse_lines(get_lines(inputfile),outputdir)
    if json:
        produceJSON(outputdir,get_lines(inputfile))

#Opens input file and produces lines from content
def get_lines(rfile):
    results = open(f'{rfile}','r')
    lines = results.readlines()
    results.close()

    return lines

def parse_lines(lines, ddir):
    for line in lines:
        #Ignores only status lines in the gnmap
        if 'Status' not in line:
            #Split each line into two entries (IP section, ports section)
            parts = (line.split("()"))
            if len(parts) > 1:
                #Finds only the IP address in the IP section
                host = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", parts[0])
                #open file for writing list of live hosts
                if not os.path.exists(f'{ddir}/hosts'):
                    os.makedirs(f'{ddir}/hosts')
                with open(f'{ddir}/livehosts.txt', 'a') as livefile, open(f'{ddir}/hosts/{host[0]}.txt', 'a') as hostfile:
                    #write the IP address to the file
                    livefile.writelines(f"{host[0]}\n")
                    #Splits the ports section based on comma delimation 
                    ports = parts[1].split(", ")
                    #iterate through list of ports
                    for p in ports:
                        #Tidy up the data
                        port = p.replace("\tPorts: ",'')
                        port = re.findall(r"^\d{1,5}",port)
                        #ignore hosts with no ports open
                        if len(port)>=1:
                            #open cooresponding port file to add IP to
                            hostfile.writelines(f'{port[0]}\n')
                            portfile = open(f'{ddir}/{port[0]}.txt', 'a')
                            #Add entry 
                            portfile.writelines(f"{host[0]}:{port[0]}\n")
                            #check if the port is a known web port
                            if int(port[0]) in [80, 8080, 443] or int(port[0]) > 1025:
                                #open web file
                                with open(f'{ddir}/web.txt', 'a') as web:
                                    #write entry
                                    web.writelines(f"{host[0]}:{port[0]}\n")
                            #check if the port is a known ephemeral port
                            if int(port[0]) > 1025:
                                #open web file
                                with open(f'{ddir}/ephemeral.txt', 'a') as eph:
                                    #write entry
                                    eph.writelines(f"{host[0]}:{port[0]}\n")

def produceJSON(ddir, lines):
    hostDict = {'boards':[
        {
            "name": "Investigate",
            "lists": [{
                "name": "To-Review",
                "cards": [

                ]
            }]
        }
    ]}

    for line in lines:
        #Ignores only status lines in the gnmap
        if 'Status' not in line:
            #Split the line line into two entries (IP section, ports section)
            parts = (line.split("()"))
            #Only include the host if it has open ports
            if len(parts) > 1:
                innerDict = {}
                #Finds only the IP address in the IP section
                host = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", parts[0])
                innerDict['name'] = host[0]
                innerDict['tasks'] = []
                #Splits the ports section based on comma delimation 
                ports = parts[1].split(", ")
                #iterate through list of ports
                for p in ports:
                    #Tidy up the data
                    port = p.replace("\tPorts: ",'')
                    port = re.findall(r"^\d{1,5}",port)
                    innerDict['tasks'].append(port[0])
                hostDict['boards'][0]['lists'][0]['cards'].append(innerDict)
    with open(f'{ddir}/output.json', 'a') as output:
        json.dump(hostDict, output, indent = 4)

if __name__ == "__main__":
    main(sys.argv[1:])
