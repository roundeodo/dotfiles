# NPC RTL selection naming

For NPC xbar routing, name the operation `select`, not the generic implementation
term `decode`.

- `write_slave_select_addr`: address currently used to select the write target.
- `select_slaves_by_addr()`: forms the slave selection vector from an address.
- `read_slave_select_index`: current combinational read target index.
- `read_selected_slave_index_q`: target index retained after the handshake.

Names should describe the architectural operation and the information currently
carried by the signal. Do not expose an implementation-stage term when it does
not help identify the signal's purpose.
