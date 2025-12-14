import argparse
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, cast

from lark import Lark, Transformer
from lark.exceptions import LarkError


@dataclass(frozen=True)
class Instr:
    op: str
    A: int
    B: int
    C: int
    D: Optional[int] = None


class IRBuilder(Transformer):
    def INT(self, t):
        return int(str(t))

    def instruction(self, items):
        return items[0]

    def load(self, items):
        A, B, C = items
        return Instr(op="LOAD", A=A, B=B, C=C)

    def read(self, items):
        A, B, C, D = items
        return Instr(op="READ", A=A, B=B, C=C, D=D)

    def write(self, items):
        A, B, C, D = items
        return Instr(op="WRITE", A=A, B=B, C=C, D=D)

    def uminus(self, items):
        A, B, C = items
        return Instr(op="UMINUS", A=A, B=B, C=C)

    def start(self, items):
        return [x for x in items if x is not None]


class UVMAssembler:
    def __init__(self, grammar_path: str = "grammar.lark"):
        grammar = Path(grammar_path).read_text(encoding="utf-8")
        self.parser = Lark(grammar, start="start", parser="lalr", transformer=IRBuilder())

    def assemble_to_ir(self, text: str) -> List[Instr]:
        try:
            return cast(List[Instr], self.parser.parse(text))
        except LarkError as e:
            raise SyntaxError(f"Синтаксическая ошибка: {e}")

    def encode(self, ir: List[Instr]) -> bytes:
        out = bytearray()
        for ins in ir:
            out.extend(self._encode_one(ins))
        return bytes(out)

    def _encode_one(self, ins: Instr) -> bytes:
        if ins.op == "LOAD":
            return self._pack6(ins.A, ins.B, ins.C)
        if ins.op == "UMINUS":
            return self._pack6(ins.A, ins.B, ins.C)
        if ins.op == "READ":
            if ins.D is None:
                raise ValueError("READ требует D")
            return self._pack7(ins.A, ins.B, ins.C, ins.D)
        if ins.op == "WRITE":
            if ins.D is None:
                raise ValueError("WRITE требует D")
            return self._pack7(ins.A, ins.B, ins.C, ins.D)
        raise ValueError(f"Неизвестная команда: {ins.op}")

    @staticmethod
    def _pack6(A: int, B: int, C: int) -> bytes:
        if not (0 <= A < (1 << 7)):
            raise ValueError("A вне диапазона 7 бит")
        if not (0 <= B < (1 << 17)):
            raise ValueError("B вне диапазона 17 бит")
        if not (0 <= C < (1 << 23)):
            raise ValueError("C вне диапазона 23 бит")
        word = (A & 0x7F) | ((B & 0x1FFFF) << 7) | ((C & 0x7FFFFF) << 24)
        return word.to_bytes(6, byteorder="little", signed=False)

    @staticmethod
    def _pack7(A: int, B: int, C: int, D: int) -> bytes:
        if not (0 <= A < (1 << 7)):
            raise ValueError("A вне диапазона 7 бит")
        if not (0 <= B < (1 << 17)):
            raise ValueError("B вне диапазона 17 бит")
        if not (0 <= C < (1 << 17)):
            raise ValueError("C вне диапазона 17 бит")
        if not (0 <= D < (1 << 14)):
            raise ValueError("D вне диапазона 14 бит")
        word = (A & 0x7F) | ((B & 0x1FFFF) << 7) | ((C & 0x1FFFF) << 24) | ((D & 0x3FFF) << 41)
        return word.to_bytes(7, byteorder="little", signed=False)


def main():
    ap = argparse.ArgumentParser(description="Assembler for UVM (variant 14)")
    ap.add_argument("-i", "--input", required=True)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()

    src = Path(args.input).read_text(encoding="utf-8")
    asm = UVMAssembler()
    ir = asm.assemble_to_ir(src)

    if args.test:
        for i, ins in enumerate(ir):
            d = asdict(ins)
            d = {k: v for k, v in d.items() if v is not None}
            print(f"{i}: {d}")
        return

    data = asm.encode(ir)
    Path(args.output).write_bytes(data)


if __name__ == "__main__":
    main()
