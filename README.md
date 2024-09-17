# beholder

Beholder is a Python script for handling and parsing GNMAP files, making it more efficient to feed data to other tools.

## Features

- Parses GNMAP files and extracts relevant information
- Generates separate files for live hosts, individual hosts, and specific ports
- Creates a special file for web ports (80, 8080, 443, and ports > 1025)
- Generates a file for ephemeral ports (ports > 1025)
- Optional JSON output for easy integration with other tools

## Usage

```bash 
python beholder.py -i <input_GNMAP_file> -o <output_directory> [-j]
```


### Options:

- `-i`, `--ifile`: Specify the input GNMAP file (required)
- `-o`, `--ofile`: Specify the output directory (required)
- `-j`, `--json`: Generate JSON output (optional)

## Output

Beholder generates the following files in the specified output directory:

- `livehosts.txt`: List of all live hosts
- `<port>.txt`: Files for each discovered port, containing "IP:port" entries
- `web.txt`: List of potential web services (ports 80, 8080, 443, and > 1025)
- `ephemeral.txt`: List of ephemeral ports (> 1025)
- `hosts/<IP>.txt`: Individual files for each host, listing open ports
- `output.json`: JSON output (if `-j` option is used)

## Example

```bash
python beholder.py -i scan_results.gnmap -o parsed_results -j
```


This command will parse the `scan_results.gnmap` file, save the results in the `parsed_results` directory, and generate a JSON output.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.