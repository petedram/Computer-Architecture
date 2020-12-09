"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        #hold 256 bytes of memory and 8 general-purpose registers.
        self.ram = [00000000] * 256 #256 bytes of mem
        self.reg = [0] * 8 #8 bytes of registers
        self.pc = 0 #program counter
        self.running = False
        #The SP points at the value at the top of the stack (most recently pushed), or at address `F4` if the stack is empty.
        self.sp = 7 #R7


    def load(self):
        """Load a program into memory."""
        
        if len(sys.argv) !=2:
            print("don't forget to add file name")
            raise ValueError

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    item_split = line.split('#')
                    value = item_split[0].strip()
                    if value == '':
                        continue
                    num = int(value,2)
                    self.ram[address] = num
                    address +=1
        
        except FileNotFoundError:
            print('file not found')
            raise ValueError


        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    #`ram_read()` should accept the address to read and return the value stored there.
    def ram_read(self, MAR):
        MDR = self.ram[MAR]

        return MDR

    # `ram_write()` should accept a value to write, and the address to write it to.
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110

        self.pc = 0
        self.running = True

        while self.running:
            IR = self.ram_read(self.pc)
    
            operand_a = self.ram_read(self.pc +1)
            operand_b = self.ram_read(self.pc +2)

            if IR == HLT:
                self.running = False
                sys.exit(1)

            elif IR == LDI:
                self.reg[operand_a] = operand_b
                self.pc +=3

            elif IR == PRN:
                print(self.reg[operand_a])
                self.pc +=2

            elif IR == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc +=3

            elif IR == PUSH:
                #Decrement the `SP`.
                self.reg[self.sp] -= 1

                #Copy the value in the given register to the address pointed to by `SP`.
                val = self.reg[operand_a]
                self.ram[self.reg[self.sp]] = val
                self.pc += 2

            elif IR == POP:
                reg = operand_a
                val = self.ram[self.reg[self.sp]]
                # Copy the value from the address pointed to by `SP` to the given register.
                self.reg[reg] = val
                # Increment `SP`.
                self.reg[self.sp] +=1
                self.pc +=2



