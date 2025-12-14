from assembler import UVMAssembler


def test_load():
    asm = UVMAssembler()
    ir = asm.assemble_to_ir("LOAD 82, 724, 741\n")
    data = asm.encode(ir)
    assert data == bytes([0x52, 0x6A, 0x01, 0xE5, 0x02, 0x00])


def test_read():
    asm = UVMAssembler()
    ir = asm.assemble_to_ir("READ 25, 186, 449, 171\n")
    data = asm.encode(ir)
    assert data == bytes([0x19, 0x5D, 0x00, 0xC1, 0x01, 0x56, 0x01])


def test_write():
    asm = UVMAssembler()
    ir = asm.assemble_to_ir("WRITE 57, 805, 819, 873\n")
    data = asm.encode(ir)
    assert data == bytes([0xB9, 0x92, 0x01, 0x33, 0x03, 0xD2, 0x06])


def test_uminus():
    asm = UVMAssembler()
    ir = asm.assemble_to_ir("UMINUS 33, 600, 596\n")
    data = asm.encode(ir)
    assert data == bytes([0x21, 0x2C, 0x01, 0x54, 0x02, 0x00])
