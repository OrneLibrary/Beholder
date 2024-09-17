import os
import sys
import getopt
import re
import json
from typing import List, Dict

def main(argv: List[str]) -> None:
    inputfile = ''
    outputdir = ''
    json_output = False

    try:
        opts, _ = getopt.getopt(argv, "hi:o:j", ["ifile=", "ofile=", "json"])
    except getopt.GetoptError:
        print('usage: beholder.py -i <input_file> -o <output_directory>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('usage: beholder.py -i <input_GNMAP_file> -o <output_directory>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            if not os.path.exists(arg):
                print(f'Error: {arg} does not exist')
                sys.exit(2)
            if not arg.endswith('.gnmap'):
                print('Error: Incorrect file type\nPlease provide a .gnmap file')
                sys.exit(2)
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            if not os.path.isdir(arg):
                print(f'Error: No such directory\n{arg} does not exist')
                sys.exit(2)
            outputdir = arg
        elif opt in ("-j", "--json"):
            json_output = True

    lines = get_lines(inputfile)
    parse_lines(lines, outputdir)
    if json_output:
        produce_json(outputdir, lines)

def get_lines(rfile: str) -> List[str]:
    with open(rfile, 'r') as results:
        return results.readlines()

def parse_lines(lines: List[str], ddir: str) -> None:
    os.makedirs(os.path.join(ddir, 'hosts'), exist_ok=True)
    
    for line in lines:
        if 'Status' in line:
            continue

        parts = line.split("()")
        if len(parts) <= 1:
            continue

        host = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", parts[0])
        if not host:
            continue

        host = host[0]
        with open(os.path.join(ddir, 'livehosts.txt'), 'a') as livefile, \
             open(os.path.join(ddir, 'hosts', f'{host}.txt'), 'a') as hostfile:
            livefile.write(f"{host}\n")
            
            ports = parts[1].split(", ")
            for p in ports:
                port = re.findall(r"^\d{1,5}", p.replace("\tPorts: ", ''))
                if not port:
                    continue
                
                port = port[0]
                hostfile.write(f'{port}\n')
                
                with open(os.path.join(ddir, f'{port}.txt'), 'a') as portfile:
                    portfile.write(f"{host}:{port}\n")
                
                port_num = int(port)
                if port_num in [80, 8080, 443] or port_num > 1025:
                    with open(os.path.join(ddir, 'web.txt'), 'a') as web:
                        web.write(f"{host}:{port}\n")
                
                if port_num > 1025:
                    with open(os.path.join(ddir, 'ephemeral.txt'), 'a') as eph:
                        eph.write(f"{host}:{port}\n")

def produce_json(ddir: str, lines: List[str]) -> None:
    host_dict: Dict = {
        'boards': [{
            "name": "Investigate",
            "lists": [{
                "name": "To-Review",
                "cards": []
            }]
        }]
    }

    for line in lines:
        if 'Status' in line:
            continue

        parts = line.split("()")
        if len(parts) <= 1:
            continue

        host = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", parts[0])
        if not host:
            continue

        inner_dict = {
            'name': host[0],
            'tasks': [
                re.findall(r"^\d{1,5}", p.replace("\tPorts: ", ''))[0]
                for p in parts[1].split(", ")
                if re.findall(r"^\d{1,5}", p.replace("\tPorts: ", ''))
            ]
        }
        host_dict['boards'][0]['lists'][0]['cards'].append(inner_dict)

    with open(os.path.join(ddir, 'output.json'), 'w') as output:
        json.dump(host_dict, output, indent=4)

if __name__ == "__main__":
    main(sys.argv[1:])
