"""Command line interface for Clew PDF ingestion, originally authored by Alexandra Pletea."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markup import escape

from .engine import IngestionEngine, _document_slug

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
    """Ingest PDF materials as prose and image-first Markdown extraction artifacts."""
    try:
        if path.is_file():
            if path.suffix.lower() != ".pdf":
                raise ValueError(f"{path} is not a PDF file.")
            pdf_files = [path]
        elif path.is_dir():
            pdf_files = sorted(
                (item for item in path.iterdir() if item.is_file() and item.suffix.lower() == ".pdf"),
                key=lambda item: (item.name.casefold(), item.name),
            )
            if not pdf_files:
                console.print(f"[yellow]Warning:[/yellow] No PDF files found in {escape(str(path))}")
                raise typer.Exit(code=0)
        else:
            raise ValueError(f"Path {path} does not exist.")

        slugs: dict[str, Path] = {}
        for pdf in pdf_files:
            slug = _document_slug(pdf)
            if slug in slugs:
                raise ValueError(
                    f"Output name collision: {slugs[slug].name!r} and {pdf.name!r} both use {slug!r}. "
                    "Use separate output/assets roots or rename the input copies."
                )
            slugs[slug] = pdf
        engine = IngestionEngine(
            output_dir=str(output_dir),
            assets_dir=str(assets_dir),
            course_name=course,
            default_domain=domain,
        )
    except (OSError, ValueError) as error:
        console.print(f"[red]Error:[/red] {escape(str(error))}")
        raise typer.Exit(code=1) from error

    console.print(f"[bold green]Starting ingestion for {len(pdf_files)} document(s)...[/bold green]")
    failures = 0
    for pdf in pdf_files:
        try:
            chapters = engine.ingest_pdf(pdf)
            console.print(
                f"[green]Ingested:[/green] {escape(pdf.name)} -> [bold]{len(chapters)}[/bold] chapter file(s)"
            )
            for chapter_file, stats in chapters:
                console.print(f"  [bold]{escape(str(chapter_file))}[/bold]  [dim]{stats}[/dim]")
        except Exception as error:
            failures += 1
            console.print(f"[red]Failed {escape(pdf.name)}:[/red] {escape(str(error))}")
    if failures:
        console.print(f"[red]Ingestion finished with {failures} failed document(s).[/red]")
        raise typer.Exit(code=1)
    console.print("[bold green]Ingestion complete![/bold green]")


def main():
    app()


if __name__ == "__main__":
    main()
