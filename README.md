
# HashiCorp Doctor


HashiCorp Doctor is a diagnostics and troubleshooting tool for HashiCorp products: Vault, Consul, and Nomad.
You can use it as a standalone binary (no Python required) or as a Python CLI/Web UI tool.

## Features
- **Vault:** Seal/unseal status, leader election, replication, license, token/lease health, config validation, raft/autopilot state.
- **Consul:** Cluster state, raft peers, autopilot, gossip, leader, catalog, envoy, ACLs.
- **Nomad:** Autopilot, leader, scheduler, jobs, plugins.
- **General:** Upgrade pre-checks, snapshot validation, resource utilization.
- **HTML Report:** Generate and download a comprehensive HTML diagnostics report from CLI or Web UI.


## Quick Start (Recommended)

### 1. Download the Binary

Go to the [Releases page](https://github.com/your-username/hcp-doctor/releases) and download the binary for your OS and architecture:

- **macOS:** `hcp-doctor-mac`
- **Linux:** `hcp-doctor-linux`
- **Windows:** `hcp-doctor-win.exe`

### 2. Run the Tool

Make the binary executable (macOS/Linux):

```bash
chmod +x hcp-doctor-<platform>
./hcp-doctor-<platform> doctor
```

On Windows, just double-click or run in Command Prompt:

```
hcp-doctor-win.exe doctor
```

You can use all CLI options and the web UI as described below.

---

## Alternative: Python Virtual Environment

If you prefer, you can still use the Python version:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
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
