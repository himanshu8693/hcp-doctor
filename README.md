# Running from a Downloaded Binary Release

If you downloaded a release from the GitHub Releases page and it contains a file named `hcp-doctor-linux`, `hcp-doctor-macos`, or `hcp-doctor-windows.exe`, you can run the tool directly without installing Python or any dependencies.

## Steps to Run the Binary

1. **Download the correct binary for your OS from the GitHub Release assets:**
	- Linux: `hcp-doctor-linux`
	- macOS: `hcp-doctor-macos`
	- Windows: `hcp-doctor-windows.exe`

2. **(Linux/macOS only) Make the binary executable:**
	```sh
	chmod +x ./hcp-doctor-linux   # or ./hcp-doctor-macos
	```

3. **Run the tool:**
	- **Linux/macOS:**
	  ```sh
	  ./hcp-doctor-linux doctor --profile=dev
	  # or for macOS
	  ./hcp-doctor-macos doctor --profile=dev
	  ```
	- **Windows:**
	  ```sh
	  hcp-doctor-windows.exe doctor --profile=dev
	  ```

4. **(Optional) Set environment variables for cluster access:**
	```sh
	export VAULT_ADDR=http://your-vault:8200
	export VAULT_TOKEN=your-root-token
	export CONSUL_HTTP_ADDR=https://your-consul:8501
	export CONSUL_HTTP_TOKEN=your-consul-token
	export NOMAD_ADDR=http://your-nomad:4646
	export NOMAD_TOKEN=your-nomad-token
	```
	Or pass them as CLI arguments (see below).

5. **You should see cluster health and diagnostics output in your terminal.**

---

**Note:** If you downloaded a `.zip` file containing the source code (not a single binary), follow the instructions in the "Usage" section above to install Python and run the tool from source.

# HCP Doctor

A CLI tool to automate collection and analysis of Vault, Consul, and Nomad cluster health.

## Features

## Usage


```sh
pip install -r requirements.txt
source .venv/bin/activate  # if using a virtualenv
```

## Usage

```sh
pip install -r requirements.txt
source .venv/bin/activate  # if using a virtualenv
python cli.py doctor
```

## Web UI

You can also review all health checks in your browser:


# HCP Doctor

HCP Doctor is a cross-platform diagnostics tool for HashiCorp Vault, Consul, and Nomad clusters. It works on Linux, macOS, and Windows (Python 3.7+ required).

## Features
- Health checks for Vault, Consul, Nomad
- Cluster membership, inventory, backup, quotas, network, security
- System resource usage per node (where possible)
- CLI and Web UI
- Pretty, colorized output



## Prerequisites

- Python 3.7 or newer must be installed on your system (Linux, macOS, or Windows).
- Internet access to install dependencies via pip.
- Access to your Vault, Consul, and Nomad cluster endpoints.

## Environment Variables & CLI Arguments

You can configure the tool using environment variables or CLI arguments. These are required for the tool to connect to your clusters:

- `VAULT_ADDR` and `VAULT_TOKEN` (Vault address and token)
- `CONSUL_HTTP_ADDR` and `CONSUL_HTTP_TOKEN` (Consul address and token)
- `NOMAD_ADDR` and `NOMAD_TOKEN` (Nomad address and token)

You can set these in your shell before running the tool:

```sh
export VAULT_ADDR=http://your-vault:8200
export VAULT_TOKEN=your-root-token
export CONSUL_HTTP_ADDR=https://your-consul:8501
export CONSUL_HTTP_TOKEN=your-consul-token
export NOMAD_ADDR=http://your-nomad:4646
export NOMAD_TOKEN=your-nomad-token
```

Or pass them as CLI arguments (where supported):

```sh
hcp-doctor doctor --vault-addr=http://your-vault:8200 --vault-token=your-root-token --consul-addr=https://your-consul:8501 --consul-token=your-consul-token --nomad-addr=http://your-nomad:4646 --nomad-token=your-nomad-token
```

### 1. Clone the repository

```sh
git clone https://github.com/himanshu8693/hcp-doctor.git
cd hcp-doctor
```

### 2. (Recommended) Create a virtual environment

```sh
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies and the tool

```sh
pip install .
```

Or, after publishing to PyPI:

```sh
pip install hcp-doctor
```


## Usage


### CLI Commands (Binary or Python)

Run diagnostics for a specific product:

```bash
./hcp-doctor-<platform> vault
./hcp-doctor-<platform> consul
./hcp-doctor-<platform> nomad
```

Run diagnostics for all products:

```bash
./hcp-doctor-<platform> doctor
```

Generate an HTML report:

```bash
./hcp-doctor-<platform> doctor --html doctor_report.html
```


### Web UI

Launch the web UI:

```bash
./hcp-doctor-<platform> web
```

Or, if using Python:

```bash
python -m hashicorp_doctor.cli web
```

Open your browser to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) (default).

From the web UI, you can:
- View diagnostics for Vault, Consul, and Nomad
- View or download the HTML diagnostics report


## Environment Variables

Set these environment variables as needed for authentication and endpoint configuration:

- `VAULT_ADDR` - Vault server address (e.g. `http://127.0.0.1:8200`)
- `VAULT_TOKEN` - Vault token for authentication
- `VAULT_SKIP_VERIFY` - Set to `true` to skip SSL verification for Vault
- `CONSUL_HTTP_ADDR` - Consul server address (e.g. `http://127.0.0.1:8500`)
- `CONSUL_HTTP_TOKEN` - Consul ACL token
- `CONSUL_HTTP_SSL_VERIFY` - Set to `false` to skip SSL verification for Consul
- `NOMAD_ADDR` - Nomad server address (e.g. `http://127.0.0.1:4646`)
- `NOMAD_TOKEN` - Nomad ACL token
- `NOMAD_SKIP_VERIFY` - Set to `true` to skip SSL verification for Nomad

You can set these in your shell before running the tool:

```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=your-vault-token
export CONSUL_HTTP_ADDR=http://127.0.0.1:8500
export CONSUL_HTTP_TOKEN=your-consul-token
export NOMAD_ADDR=http://127.0.0.1:4646
export NOMAD_TOKEN=your-nomad-token
```

## Contributing

Pull requests are welcome! Please open an issue first to discuss changes.

## License

MIT
