#!/bin/sh
# Builds paper/dee-seven-tables.pdf from the Typst source (needs uv; fetches the typst package).
# The figure is read from results/seven_tables_cross.svg, so the project root is the repository.
cd "$(dirname "$0")" && uv run --no-project --with typst==0.15.0 python -c "import typst; typst.compile('dee-seven-tables.typ', output='dee-seven-tables.pdf', root='..')"
