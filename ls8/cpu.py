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
        self.fl = 0b00000000 #00000LGE

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
        #Compare - if equal, set E flag to 1, else 0.
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = self.fl | 1 #E to 1
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = self.fl | 2 #G to 1
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = self.fl | 4 #L to 1
        elif op == 'MOD':
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == 'XOR':
            self.reg[reg_a] ^ self.reg[reg_b]
        elif op == 'AND':
            self.reg[reg_a] & self.reg[reg_b]
        elif op == 'OR':
            self.reg[reg_a] | self.reg[reg_b]
        elif op == 'NOT':
            ~ self.reg[reg_a]
        elif op == 'SHL':
            self.reg[reg_a] << self.reg[reg_b]
        elif op == 'SHR':
            self.reg[reg_a] >> self.reg[reg_b]

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
        CALL = 0b01010000
        RET = 0b00010001
        JMP = 0b01010100
        ADD = 0b10100000
        CMP = 0b10100111
        JEQ = 0b01010101
        JNE = 0b01010110
        MOD = 0b10100100
        XOR = 0b10101011
        AND = 0b10101000
        OR = 0b10101010
        NOT = 0b01101001
        SHL = 0b10101100
        SHR = 0b10101101


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

            elif IR == CALL:
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = self.pc + 2
                self.pc = self.reg[operand_a]
            
            elif IR == RET:
                val = self.ram[self.reg[self.sp]] 
                self.pc = val
                self.reg[self.sp] += 1
            
            elif IR == JMP:
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = self.pc + 2
                self.pc = self.reg[operand_a]

            elif IR == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3

            elif IR == CMP:
                self.alu('CMP', operand_a, operand_b)
                self.pc += 3

            elif IR == JEQ:
                #If `equal` flag is set (true), jump to the address stored in the given register.
                if self.fl == 1 or self.fl == 3 or self.fl == 5 or self.fl == 7: #check odd
                    self.reg[self.sp] -=1
                    self.ram[self.reg[self.sp]] = self.pc + 2
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            
            elif IR == JNE:
                #If `E` flag is clear (false, 0), jump to the address stored in the given register.
                if self.fl == 0 or self.fl == 2 or self.fl == 3 or self.fl == 4: #check not 1
                    self.reg[self.sp] -=1
                    self.ram[self.reg[self.sp]] = self.pc + 2
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            elif IR == MOD:
                self.alu('MOD', operand_a, operand_b)
                self.pc += 3

            elif IR == XOR:
                self.alu('XOR', operand_a, operand_b)
                self.pc += 3

            elif IR == AND:
                self.alu('AND', operand_a, operand_b)
                self.pc += 3

            elif IR == OR:
                self.alu('OR', operand_a, operand_b)
                self.pc += 3
            
            elif IR == NOT:
                self.alu('NOT', operand_a, 0)
                self.pc += 3
            
            elif IR == SHL:
                self.alu('SHL', operand_a, operand_b)
                self.pc += 3

            elif IR == SHR:
                self.alu('SHR', operand_a, operand_b)
                self.pc += 3
