import click
from hcp_doctor.vault import check_vault_health
from hcp_doctor.consul import check_consul_health
from hcp_doctor.nomad import check_nomad_health
from hcp_doctor.general import check_general_health

@click.group()
@click.option('--vault-addr', default=None, help='Vault address (overrides VAULT_ADDR env)')
@click.option('--vault-token', default=None, help='Vault token (overrides VAULT_TOKEN env)')
@click.option('--consul-addr', default=None, help='Consul address (overrides CONSUL_HTTP_ADDR env)')
@click.option('--consul-token', default=None, help='Consul token (overrides CONSUL_HTTP_TOKEN env)')
@click.option('--nomad-addr', default=None, help='Nomad address (overrides NOMAD_ADDR env)')
@click.option('--nomad-token', default=None, help='Nomad token (overrides NOMAD_TOKEN env)')
@click.option('--profile', default='auto', type=click.Choice(['auto', 'dev', 'prod', 'custom']), help='Check profile: auto, dev, prod, custom')
@click.pass_context
def cli(ctx, vault_addr, vault_token, consul_addr, consul_token, nomad_addr, nomad_token, profile):
    """HCP Doctor: Cluster Health Diagnostics"""
    ctx.ensure_object(dict)
    ctx.obj['vault_addr'] = vault_addr
    ctx.obj['vault_token'] = vault_token
    ctx.obj['consul_addr'] = consul_addr
    ctx.obj['consul_token'] = consul_token
    ctx.obj['nomad_addr'] = nomad_addr
    ctx.obj['nomad_token'] = nomad_token
    ctx.obj['profile'] = profile

@cli.command()
@click.pass_context
def vault(ctx):
    """Check Vault health"""
    result = check_vault_health(
        addr=ctx.obj.get('vault_addr'),
        token=ctx.obj.get('vault_token'),
        profile=ctx.obj.get('profile', 'auto')
    )
    click.echo(result)

@cli.command()
@click.pass_context
def consul(ctx):
    """Check Consul health"""
    result = check_consul_health(
        addr=ctx.obj.get('consul_addr'),
        token=ctx.obj.get('consul_token'),
        profile=ctx.obj.get('profile', 'auto')
    )
    click.echo(result)

@cli.command()
@click.pass_context
def nomad(ctx):
    """Check Nomad health"""
    result = check_nomad_health(
        addr=ctx.obj.get('nomad_addr'),
        token=ctx.obj.get('nomad_token'),
        profile=ctx.obj.get('profile', 'auto')
    )
    click.echo(result)

@cli.command()
@click.pass_context
def general(ctx):
    """Check general cluster health"""
    result = check_general_health()
    click.echo(result)


@cli.command()
@click.option('--pdf', type=click.Path(), help='Generate a PDF report at the given path')
@click.pass_context
def doctor(ctx, pdf):
    """Run all health checks and diagnostics"""
    from rich.console import Console
    from rich.table import Table
    from hcp_doctor.report import generate_pdf_report
    results = {
        "vault": check_vault_health(
            addr=ctx.obj.get('vault_addr'),
            token=ctx.obj.get('vault_token'),
            profile=ctx.obj.get('profile', 'auto')
        ),
        "consul": check_consul_health(
            addr=ctx.obj.get('consul_addr'),
            token=ctx.obj.get('consul_token'),
            profile=ctx.obj.get('profile', 'auto')
        ),
        "nomad": check_nomad_health(
            addr=ctx.obj.get('nomad_addr'),
            token=ctx.obj.get('nomad_token'),
            profile=ctx.obj.get('profile', 'auto')
        ),
    "general": check_general_health()
    }
    if pdf:
        generate_pdf_report(pdf, results["vault"], results["consul"], results["nomad"], results["general"])
        click.echo(f"PDF report generated at {pdf}")
        return
    console = Console()
    def print_section(title, result):
        console.rule(f"[bold blue]{title}")
        status = result.get("status", "unknown")
        if status == "ok":
            console.print(f"Status: [green]{status}[/green]")
        elif status == "fail":
            console.print(f"Status: [red]{status}[/red]")
        else:
            console.print(f"Status: [yellow]{status}[/yellow]")
        if result.get("warnings"):
            console.print("Warnings:")
            for w in result["warnings"]:
                console.print(f"  [yellow]- {w}[/yellow]")
        if result.get("details"):
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Detail")
            for d in result["details"]:
                table.add_row(str(d))
            console.print(table)
        console.print("")
    print_section("Vault", results["vault"])
    print_section("Consul", results["consul"])
    print_section("Nomad", results["nomad"])
    print_section("General", results["general"])

if __name__ == "__main__":
    cli()
