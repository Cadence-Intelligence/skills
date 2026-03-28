# CC-Viz

Turn complex terminal output into styled HTML pages that open in the browser. Architecture diagrams, diff reviews, data tables, slide decks: all self-contained files, no build step.

**Activates when:** You ask for a diagram, architecture overview, diff review, plan review, or are about to get a complex table in the terminal (4+ rows or 3+ columns, handled automatically without being asked).

**Example usage:**

"Draw a diagram of our authentication flow"
"Give me an architecture overview of this codebase"
"/diff-review"
"/plan-review ~/docs/refactor-plan.md"

- 11 diagram types: Mermaid for connections (flowcharts, sequences, ER, state machines, mind maps), CSS Grid for architecture overviews, HTML tables for data, Chart.js for dashboards
- Proactive table rendering: auto-converts complex terminal tables to HTML
- Six slash commands: `/diff-review`, `/plan-review`, `/generate-slides`, `/project-recap`, `/generate-web-diagram`, `/fact-check`
- Anti-slop enforcement: forbidden fonts, colors, and layout patterns baked in (no Inter, no violet gradients, no glowing cards)

## Install

```bash
/plugin install cc-viz@cadence
```

Or manually:

```bash
git clone https://github.com/Cadence-Intelligence/skills.git
cd skills && ./install.sh cc-viz
```

## License

CC BY-NC 4.0, Cadence Intelligence, 2026
