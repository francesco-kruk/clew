"""
Command Line Interface for Clew PDF Ingestion.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from .engine import IngestionEngine

app = typer.Typer(help="Clew PDF Ingestion CLI")
console = Console()


@app.command()
def ingest(
    path: Path = typer.Argument(..., help="Path to a PDF file or a directory containing PDFs"),
    output_dir: Path = typer.Option(Path("content"), "--output", "-o", help="Target directory for generated Markdown"),
    assets_dir: Path = typer.Option(Path("content/assets"), "--assets", "-a", help="Target directory for image assets"),
    course: Optional[str] = typer.Option(None, "--course", "-c", help="Course name for metadata"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Default domain for concepts"),
):
    """Ingest PDF course materials and generate modifiable Markdown artifacts in content/."""
    engine = IngestionEngine(
        output_dir=str(output_dir),
        assets_dir=str(assets_dir),
        course_name=course,
        default_domain=domain,
    )

    if path.is_file():
        if path.suffix.lower() != ".pdf":
            console.print(f"[red]Error:[/red] {path} is not a PDF file.")
            raise typer.Exit(code=1)
        pdf_files = [path]
    elif path.is_dir():
        pdf_files = list(path.glob("*.pdf")) + list(path.glob("*.PDF"))
        if not pdf_files:
            console.print(f"[yellow]Warning:[/yellow] No PDF files found in {path}")
            raise typer.Exit(code=0)
    else:
        console.print(f"[red]Error:[/red] Path {path} does not exist.")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Starting ingestion for {len(pdf_files)} document(s)...[/bold green]")

    for pdf in pdf_files:
        try:
            output_file, stats = engine.ingest_pdf(pdf)
            console.print(f"[green]✓ Ingested:[/green] {pdf.name} -> [bold]{output_file}[/bold]")
            console.print(f"  [dim]Artifacts: {stats}[/dim]")
        except Exception as e:
            console.print(f"[red]✗ Failed {pdf.name}:[/red] {e}")

    console.print("[bold green]Ingestion complete![/bold green]")


def main():
    app()


if __name__ == "__main__":
    main()
