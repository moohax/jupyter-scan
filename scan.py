import argparse
import concurrent.futures
import requests
from rich.table import Table
from rich import print

def detect_jupyter(host, port):
    url = f"http://{host}:{port}/"
    response = requests.get(url)

    if response.status_code == 200 and "Jupyter" in response.text:
        requires_auth = "password" in response.text or "login" in response.text
        return { "host": host, "port": port, "name": "jupyter-server", "requires_auth": requires_auth }


if __name__ == "__main__":
# Parse the command-line arguments
	parser = argparse.ArgumentParser(description="Detect Jupyter servers")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("host", nargs="+", help="The hostname or IP address of the target host(s)")
	group.add_argument("-f", "--file", help="A file containing a list of hostnames or IP addresses to scan, one per line")
	parser.add_argument("-p", "--port", type=int, nargs="+", default=[8888], help="The port(s) to scan (default: 8888)")
	args = parser.parse_args()

	# Read the list of hosts from the file, if specified
	if args.file:
		with open(args.file, "r") as f:
			hosts = [line.strip() for line in f]
	else:
		hosts = args.host

	# Test the function with multiple hosts and ports
	results = []
	with concurrent.futures.ProcessPoolExecutor() as executor:
		for port in args.port:
			results.extend(list(executor.map(detect_jupyter, hosts, [port] * len(hosts))))

	# Display the results in a table
	table = Table(title="Jupyter Server Detection Results")
	table.add_column("Host", style="bold")
	table.add_column("Port", style="bold")
	table.add_column("Name", style="bold")
	table.add_column("Requires Authentication", style="bold")
	for result in results:
		if result:
			table.add_row(result["host"], result["port"], result["name"], result["requires_auth"])
	print(table)
