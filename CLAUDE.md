# wiki vault — rules for the whole vault

Each subject folder keeps its own `CLAUDE.md` with its own rules. This file holds only what applies to every folder, because it is about how the vault itself renders.

## Sequence diagrams: the lines are coloured by a CSS snippet

**Obsidian's renderer, Pele, draws sequence-diagram lifelines in the theme's border colour and messages in its line colour, and nothing in the diagram source reaches them.** No `themeVariables` or other diagram setting changes those colours; under Obsidianite dark the lifelines come out `#3f3f3f`, and on a coloured `box rgba(...)` band they all but vanish. Found 2026-11-19 from a screenshot in the LLD vault, and confirmed in Pele's own source (`lib/pele.min.js` inside the Obsidian asar).

**The fix is `.obsidian/snippets/sequence-diagrams.css`**, scoped to `svg.pele-sequence` so no other diagram type changes: near-white solid messages, dashed slate lifelines, blue activation bars, amber `alt`/`loop`/`opt` frames, a red destruction X, and any `box` band tint lightened to about 0.45 of its written opacity, with a matching light-theme set. It has to be switched on under Settings → Appearance → CSS snippets. So write the diagram source normally and leave the line colours to the snippet. `.obsidian/` is gitignored here, so the same file is kept by hand in the wiki, AI, DevOps and LLD vaults. **Without the snippet enabled, the lifelines are close to invisible.**

## Plugins: Advanced Tables is on

**Community plugins enabled in this vault: Excalidraw and Advanced Tables (0.23.2, switched on 2026-11-19).** Advanced Tables changes editing, not rendering: Tab moves between cells, and the plugin pads every cell so the pipes line up in source. A plain markdown table reads the same with or without it. So any table written here is kept aligned the way the plugin would format it (cells padded to the widest in each column, a numeric column right-aligned with `--:`), which means editing a table by hand in Obsidian produces no reformatting churn. `.obsidian/` is gitignored, so plugins are installed per vault: Low Level Design also has Advanced Tables plus Codeblock Customizer, while DevOps and AI have neither.

**The daily log in `log/` is written as tables because of this.** Each `## Day DD Mon` heading carries one table with the columns Time, Tags, What and Min. Min holds the minutes of a closed range and is blank for an open `onwards` row. A row can carry two tags (`#WORK #DEVOPS`), and when hours are totalled it counts under each tag but once in the day's total. The full format and its rules belong to the `/logging` command in `~/.claude/commands/logging.md`, so change them there rather than here. November 2026 was converted from the older one-line-per-entry format on 2026-11-19, with all 44 entries checked identical.
