# TODO placement preference

The user strongly prefers TODO comments to be placed immediately above the exact code location that should be modified. A TODO should not merely describe work somewhere else in the file. The user should be able to write the required code in the next few lines directly below the TODO without searching.

When writing educational TODOs:
- Put the concrete code insertion point first.
- Keep any detailed explanation close, but do not separate the TODO from the code location.
- For skeletons, include commented code directly under the TODO when useful.
- For software-side TODOs, give more detailed hints than RTL TODOs, but still keep the actual insertion point directly below the TODO.
- For RTL TODOs, keep hints concise and positioned next to the relevant signal, always block, assignment, port, or module instance.

This applies especially to the ysyx NPC work under `/home/yong/ysyx/ysyx-workbench/npc`.
