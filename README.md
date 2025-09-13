# HCP Doctor

HCP Doctor is a cross-platform diagnostics tool for HashiCorp Vault, Consul, and Nomad clusters. It works on Linux, macOS, and Windows (Python 3.7+ required).

---

## 🚀 Quick Start: Using the Released Binary

1. **Download the correct binary for your OS from the GitHub Releases page:**
   - Linux: `hcp-doctor-linux`
   - macOS: `hcp-doctor-macos`
   - Windows: `hcp-doctor-windows.exe`

2. **(Linux/macOS only) Make the binary executable:**
   ```sh
   chmod +x ./hcp-doctor-linux   # or ./hcp-doctor-macos
   ```

3. **Set environment variables for cluster access (or pass as CLI args):**
   ```sh
   export VAULT_ADDR=http://your-vault:8200
   export VAULT_TOKEN=your-root-token
   export CONSUL_HTTP_ADDR=https://your-consul:8501
   export CONSUL_HTTP_TOKEN=your-consul-token
   export NOMAD_ADDR=http://your-nomad:4646
   export NOMAD_TOKEN=your-nomad-token
   ```

4. **Run diagnostics:**
   ```sh
   ./hcp-doctor-<platform> doctor
   ./hcp-doctor-<platform> vault
   ./hcp-doctor-<platform> consul
   ./hcp-doctor-<platform> nomad
   ./hcp-doctor-<platform> doctor --html doctor_report.html
   ./hcp-doctor-<platform> web
   ```

5. **Open the Web UI:**
   - Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser after running the `web` command.

---

## 🐍 Running from Source (Python)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/himanshu8693/hcp-doctor.git
   cd hcp-doctor
   ```
2. **(Recommended) Create a virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run diagnostics:**
   ```sh
   python -m hashicorp_doctor.cli doctor
   python -m hashicorp_doctor.cli vault
   python -m hashicorp_doctor.cli consul
   python -m hashicorp_doctor.cli nomad
   python -m hashicorp_doctor.cli doctor --html doctor_report.html
   python -m hashicorp_doctor.cli web
   ```

---

## 🧪 Automated Testing

- All CLI and Web UI functionality is covered by automated tests in the `tests/` directory.
- To run all tests:
  ```sh
  .venv/bin/python -m pytest tests/ --maxfail=3 --disable-warnings -v
  ```
- Ensure all dependencies in `requirements.txt` are installed in your environment.

---

## ⚙️ Environment Variables

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

```sh
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=your-vault-token
export CONSUL_HTTP_ADDR=http://127.0.0.1:8500
export CONSUL_HTTP_TOKEN=your-consul-token
export NOMAD_ADDR=http://127.0.0.1:4646
export NOMAD_TOKEN=your-nomad-token
```

---

## 📦 Features
- Health checks for Vault, Consul, Nomad
- Cluster membership, inventory, backup, quotas, network, security
- System resource usage per node (where possible)
- CLI and Web UI
- Pretty, colorized output
- HTML report generation and download

---

## 🤝 Contributing
Pull requests are welcome! Please open an issue first to discuss changes.

## 📝 License
MIT
