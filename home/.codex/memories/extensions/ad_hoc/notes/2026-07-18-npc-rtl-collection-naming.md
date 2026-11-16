# NPC RTL collection naming

For `ysyx-workbench/npc/vsrc/riscv32`, names must expose both hardware meaning and
data shape when shape changes interpretation.

- A packed collection with one semantic entry per object must include `_vector`.
- An unpacked collection must include `_array` when omission could look scalar.
- A single encoded element number must include `_index`.
- Name signals by the information they currently carry, not merely by the input
  that generated them or by an encoding detail such as `onehot`.
- Encoding constraints belong in comments and assertions unless consumers
  specifically depend on that encoding.
- Conversion function names should identify both the input basis and output
  meaning, for example `decode_addr_to_slave_select_vector` and
  `slave_select_vector_to_index`.
- Rename code, TODOs, comments, assertions, and debug labels together.

Examples:

- `read_slave_select_vector`: one selection bit per slave.
- `decoded_read_slave_index`: one combinationally decoded slave number.
- `read_selected_slave_index_q`: the registered slave number retained for a
  transaction.
