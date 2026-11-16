# NPC RTL event-history naming

For stored event history in `ysyx-workbench/npc/vsrc/riscv32`, use
`_occurred_q/_occurred_d` rather than `_done_q/_done_d`.

`occurred` records whether the named event happened during the current
transaction. Avoid `done` when the bit does not mean that the entire operation
completed successfully.

Example:

- `selected_slave_aw_handshake_occurred_q`
- `selected_slave_w_handshake_occurred_q`
