# write functions for action symbols
# management stack and ...
# semantic
# change symbol table generated by scanner in the SymbolTable class
# parse change to call semantic analyzer and code generator
# create output file
"""
1    assign             done
1    declare_id         done
1    declare_array      done
1    push_type          done
2    do_op              done
2    mult               done
2    push_op            done
1    label              done
1    until              done
2    array_calc         done
2    jpf_save           done
2    save               done
2    jp                 done
1    print              done
1    push_num           done
2    id                 done
    add_scope           done
    start_call ***
    counter_up ***
    break_check         done
    end_scope           done
    check_not_void      removed - it is checked in declare_id
    end_call ***
    add_param           done
    end_func_params     done
    start_func          done
    declare_entry_array done
"""

'''
things to be done for the 4th phase:

define a new stack for activation records
    argument push   #copy or pure
    return
    jump to main
'''

from symbol_table import SymbolTable
from heap_manager import HeapManager

kind_key = "kind"
type_key = "type"
address_key = "address"
scope_key = "scope"
attributes_key = "attributes"
lexeme_key = "lexeme"
invocation_address_key = "invocation_address"
return_address_key = "return_address"
return_value_key = "return_value"


class SemanticAnalyzer:
    def __init__(self):
        self.num_semantic_errors = 0
        self.all_errors = []

    def raise_semantic_error(self, line_no, error="error", first_op="", second_op="", third_op="", fourth_op=""):
        self.all_errors.append(error.format(line_no, first_op, second_op, third_op, fourth_op))
        self.num_semantic_errors += 1

    def pop_error(self):
        # if we declare a function of type void we must pop the error
        self.all_errors.pop()
        self.num_semantic_errors -= 1


def get_type_name(tuple_type):
    if tuple_type[1]:
        return "array"
    else:
        return tuple_type[0]


class CodeGenerator:

    def __init__(self, symbol_table: SymbolTable, heap: HeapManager):
        self.symbol_table = symbol_table
        self.semantic_stack = []
        self.PB = []
        self.FS = []
        # pc shows the next line of program block to be filled (i in slides)
        self.PC = 0
        self.heap_manager = heap
        self.current_line = 0
        # used to say that the function doesn't take any more arguments.
        # in end_call it will go back to False but in arg_input it may go True if we have error_num_args
        self.no_more_arg_input = False
        # for semantic stack
        # todo must be changed in future because lookup must search by scope - can be removed now.
        #  we don't need start_ind in lookup function any more
        self.start_scope = 0

        self.num_open_repeats = 0

        self.semantic_analyzer = SemanticAnalyzer()
        # errors
        self.error_scoping = "#{0}: Semantic Error! '{1}' is not defined.{2}{3}{4}"
        self.error_void_type = "#{0}: Semantic Error! Illegal type of void for '{1}'.{2}{3}{4}"
        self.error_type_missmatch = "#{0}: Semantic Error! Type mismatch in operands, Got {1} instead of {2}.{3}{4}"
        self.error_break = "#{0}: Semantic Error! No 'repeat ... until' found for 'break'."
        self.error_param_type_missmatch = "#{0}: Semantic Error! Mismatch in type of argument {1} of '{2}'. Expected '{3}' but got '{4}' instead."
        self.error_num_args = "#{0}: Semantic Error! Mismatch in numbers of arguments of '{1}'.{2}{3}{4}"

    def code_gen(self, action_symbol, token, line_number):
        self.current_line = line_number
        if self.no_more_arg_input and action_symbol != "#end_call":
            return

        action_symbol = action_symbol[1:]
        if action_symbol == "declare_id":
            self.declare_id(token)
        elif action_symbol == "declare_array":
            self.declare_array(token)
        elif action_symbol == "push_type":
            self.push_type(token)
        elif action_symbol == "do_op":
            self.do_op(token)
        # elif action_symbol == "mult":
        #     self.mult(token)
        elif action_symbol == "push_op":
            self.push_op(token)
        elif action_symbol == "label":
            self.label(token)
        elif action_symbol == "until":
            self.until(token)
        elif action_symbol == "array_calc":
            self.array_calc(token)
        elif action_symbol == "jpf_save":
            self.jpf_save(token)
        elif action_symbol == "save":
            self.save(token)
        elif action_symbol == "jp":
            self.jp(token)
        elif action_symbol == "print":
            self.print(token)
        elif action_symbol == "push_num":
            self.push_num(token)
        elif action_symbol == "id":
            self.id(token)
        elif action_symbol == "assign":
            self.assign(token)
        elif action_symbol == "push_eq":
            self.push_eq(token)
        elif action_symbol == "break":
            self.break_check(token)
        elif action_symbol == "add_scope":
            self.add_scope(token)
        elif action_symbol == "start_func":
            self.start_func(token)
        elif action_symbol == "add_param":
            self.add_param(token)
        elif action_symbol == "end_func_params":
            self.end_func_params(token)
        elif action_symbol == "start_call":
            self.start_call(token)
        elif action_symbol == "end_call":
            self.end_call(token)
        elif action_symbol == "declare_entry_array":
            self.declare_entry_array(token)
        elif action_symbol == "return":
            self.return_command(token)
        elif action_symbol == "return_manual":
            self.return_manual(token)
        elif action_symbol == "arg_input":
            self.arg_input(token)
        elif action_symbol == "end_scope":
            self.end_scope(token)
        elif action_symbol == "push_function":
            self.push_function(token)
        elif action_symbol == "pop_function":
            self.pop_function(token)
        elif action_symbol == "set_function_info":
            self.set_function_info(token)
        elif action_symbol == "call_main":
            self.call_main(token)
        elif action_symbol == "jump_out":
            self.jump_out(token)
        elif action_symbol == "show_scope_start":
            self.show_scope_start(token)
        elif action_symbol == "pop_scope":
            self.pop_scope(token)

    def pop_last_n(self, n):
        # pop last n elements from semantic stack
        for _ in range(n):
            self.semantic_stack.pop()

    @staticmethod
    def get_pb_line(line_index, operation, first_op=" ", second_op=" ", third_op=" "):
        return f'{line_index}\t({operation}, {first_op}, {second_op}, {third_op} )'

    def program_block_insert(self, operation, first_op=" ", second_op=" ", third_op=" "):
        # insert to program block
        operation = self.get_operation_by_symbol(operation)
        self.PB.append(self.get_pb_line(len(self.PB), operation, first_op, second_op, third_op))
        self.PC += 1

    def program_block_modification(self, index, operation, first_op="", second_op="", third_op=""):
        # modify a passed line of program block and add the code
        operation = self.get_operation_by_symbol(operation)
        self.PB[index] = self.get_pb_line(index, operation, first_op, second_op, third_op)

    def program_block_insert_empty(self):
        self.PB.append("")
        self.PC += 1

    @staticmethod
    def get_operation_by_symbol(symbol):
        if symbol == '+':
            return "ADD"
        elif symbol == '-':
            return "SUB"
        elif symbol == '*':
            return "MULT"
        elif symbol == "==":
            return "EQ"
        elif symbol == "<":
            return "LT"
        elif symbol == ":=":
            return "ASSIGN"
        else:
            return symbol.upper()

    def add_scope(self, token):
        # add scope to scope stack
        self.symbol_table.add_scope()

    def end_scope(self, token=""):
        self.symbol_table.end_scope()

    def return_command(self, token):
        function_row_index = self.FS[-1]
        function_row = self.symbol_table.get_row_by_id(function_row_index)
        return_type = function_row[type_key]
        if return_type != "void":
            return_value = self.semantic_stack.pop()
            return_value_temp_address = function_row[return_value_key]
            self.program_block_insert(
                operation=":=",
                first_op=return_value,
                second_op=return_value_temp_address
            )
        self.program_block_insert(
            operation="JP",
            first_op="@" + str(function_row[return_address_key])
        )

    def return_manual(self, token):
        function_row_index = self.FS[-1]
        function_row = self.symbol_table.get_row_by_id(function_row_index)
        self.program_block_insert(
            operation="JP",
            first_op="@" + str(function_row[return_address_key])
        )

    def start_func(self, token):
        # start of function declaration
        self.symbol_table.modify_kind_last_row("func")
        # add the row_id of function in symbol table to stack so
        # we can modify num attributes of this function later
        self.semantic_stack.append(self.symbol_table.get_id_last_row())
        if self.symbol_table.get_last_row()['type'] == "void":
            self.semantic_analyzer.pop_error()
        self.add_scope(token)
        # add the counter for parameters
        self.semantic_stack.append(0)

    def add_param(self, token):
        self.symbol_table.modify_kind_last_row("param")
        counter = self.semantic_stack.pop()
        counter += 1
        self.semantic_stack.append(counter)

    def declare_entry_array(self, token):
        self.push_num("0")
        self.declare_array(token)

    def end_func_params(self, token):
        # end of function declaration
        self.symbol_table.modify_attributes_row(row_id=self.semantic_stack[-2],
                                                num_attributes=self.semantic_stack[-1],
                                                arr_func=False)
        self.pop_last_n(2)

    def start_call(self, token):
        # start of function call
        # row_id = self.symbol_table.lookup(self.semantic_stack[-1])['id']
        function_row_id = self.symbol_table.get_row_id_by_address(self.semantic_stack[-1])
        self.semantic_stack.pop()
        num_parameters = self.symbol_table.get_row_by_id(function_row_id)[attributes_key]
        # add parameter types to stack in the form of tuple (type, is_array)
        for i in range(num_parameters, 0, -1):
            temp_address_param = self.symbol_table.get_row_by_id(function_row_id + i)[address_key]
            # type_param = self.get_operand_type(temp_address_param)
            self.semantic_stack.append(temp_address_param)

        # add the number of parameters to stack
        self.semantic_stack.append(num_parameters)
        # add a counter for arguments - at first it is equal to number of parameters
        self.semantic_stack.append(num_parameters)
        # add name of function to stack
        self.semantic_stack.append(self.symbol_table.get_row_by_id(function_row_id)[lexeme_key])

    def arg_input(self, token):
        # take input argument for function call
        if not self.no_more_arg_input:
            arg = self.semantic_stack.pop()
            type_arg = self.get_operand_type(arg)
            name_func = self.semantic_stack.pop()
            counter_args = self.semantic_stack.pop()
            counter_args -= 1
            if counter_args == 0 and token != ")":
                self.no_more_arg_input = True
                self.semantic_analyzer.raise_semantic_error(line_no=self.current_line,
                                                            error=self.error_num_args,
                                                            first_op=name_func
                                                            )

            num_parameters = self.semantic_stack.pop()
            temp_param = self.semantic_stack.pop()
            self.program_block_insert(
                operation=":=",
                first_op=arg,
                second_op=temp_param
            )

            type_param = self.get_operand_type(temp_param)
            if type_arg != type_param:
                pass
                # self.semantic_analyzer.raise_semantic_error(line_no=self.current_line,
                #                                             error=self.error_param_type_missmatch,
                #                                             first_op=num_parameters - counter_args,
                #                                             second_op=name_func,
                #                                             third_op=self.get_type_name(type_param),
                #                                             fourth_op=self.get_type_name(type_arg)
                #                                             )
            else:
                if name_func == "output":
                    self.semantic_stack.append(arg)
                    self.print("nothing")

            self.semantic_stack.append(num_parameters)
            self.semantic_stack.append(counter_args)
            self.semantic_stack.append(name_func)

    def end_call(self, token):
        # end of function call
        self.no_more_arg_input = False
        name_func = self.semantic_stack.pop()
        counter_args = self.semantic_stack.pop()
        num_parameters = self.semantic_stack.pop()
        if counter_args != 0:
            self.semantic_analyzer.raise_semantic_error(line_no=self.current_line,
                                                        error=self.error_num_args,
                                                        first_op=name_func
                                                        )
            self.pop_last_n(counter_args)

        function_row = self.symbol_table.lookup(name_func)
        index = function_row['id']
        if index in self.FS:
            self.semantic_analyzer.raise_semantic_error(1)  # todo added to avoid recursive call

        # return if function_row does not have needed keys (may not happen!)
        if invocation_address_key not in function_row or return_address_key not in function_row:
            # print("error in function declaration")
            return

        # update the return address temp of function (we want the function to return here after invocation)
        return_address_temp = function_row[return_address_key]
        self.program_block_insert(
            operation=":=",
            first_op="#" + str(self.PC + 2),
            second_op=return_address_temp
        )

        # # if the function is supposed to return a value, we need to push the address of return value to stack
        # if function_row[type_key] != "void":
        #     self.semantic_stack.append(function_row[return_value_key]

        # now that everything is set (including return address and arguments assignment), we can jump to the function
        self.program_block_insert(
            operation="JP",
            first_op=function_row[invocation_address_key]
        )
        if function_row[type_key] != "void":
            returnee_copy = self.heap_manager.get_temp(function_row[type_key])
            self.program_block_insert(
                operation=":=",
                first_op=function_row[return_value_key],
                second_op=returnee_copy
            )
            self.semantic_stack.append(returnee_copy)

    def push_type(self, token):
        # push type to stack
        if token == "int" or token == "void":
            self.semantic_stack.append(token)
        else:
            raise Exception("type not supported")

    def push_num(self, token):
        # push number to stack
        self.semantic_stack.append(str("#" + token.strip()))

    def print(self, token):
        self.program_block_insert(operation="print", first_op=self.semantic_stack[-1])
        self.semantic_stack.pop()

    def break_check(self, token):
        # check if we are in a repeat until statement
        if self.num_open_repeats == 0:
            self.semantic_analyzer.raise_semantic_error(line_no=self.current_line,
                                                        error=self.error_break)
        # push PC counter so that it can be filled in the #until action symbol to jump out
        else:
            self.semantic_stack.append(self.PC)
            self.program_block_insert_empty()
            # self.semantic_stack.insert(1, "break")
            self.semantic_stack.append("break")

    def declare_id(self, token, kind="var"):
        # search in symbol table
        # if found in current scope raise error
        # if not found
        # add to symbol table
        # token will be the lexeme of the variable
        the_row = self.symbol_table.lookup(token, self.start_scope, False)
        if the_row is not None and the_row[scope_key] == self.symbol_table.current_scope:
            # this means that the variable is already declared,
            # and we want to redefine it
            del the_row[type_key]

        self.symbol_table.insert(token)
        if self.semantic_stack[-1] == "void":
            self.semantic_analyzer.raise_semantic_error(line_no=self.current_line,
                                                        error=self.error_void_type,
                                                        first_op=token)

        self.symbol_table.modify_last_row(kind=kind, type=self.semantic_stack[-1])
        self.program_block_insert(
            operation=":=",
            first_op="#0",
            second_op=self.symbol_table.get_last_row()[address_key],
        )
        self.semantic_stack.pop()

    def declare_array(self, token):
        # add to symbol table
        array_size = self.semantic_stack.pop()
        if str(array_size).startswith("#"):
            array_size = int(array_size[1:])
        self.symbol_table.modify_attributes_last_row(num_attributes=array_size)
        array_row = self.symbol_table.get_last_row()
        # array address is the address of pointer to array
        # we need to allocate memory for the array itself and then assign the address of the first entry to the pointer
        array_address = array_row[address_key]
        entries_type = array_row[type_key]
        array_start_address = self.heap_manager.get_temp(entries_type, array_size)
        self.program_block_insert(
            operation=":=",
            first_op="#" + str(array_start_address),
            second_op=array_address
        )

    def assign(self, token):
        # stack:
        # -1: source temp
        # -2: =
        # -3: destination temp
        answer = self.semantic_stack[-3]
        self.program_block_insert(operation=":=", first_op=self.semantic_stack[-1], second_op=self.semantic_stack[-3])
        self.pop_last_n(3)
        if len(self.semantic_stack) > 0 and self.semantic_stack[-1] == "=":
            # means there was a nested assignment and we should push the result to the stack
            self.semantic_stack.append(answer)

    def label(self, token):
        # declare where to jump back after until in repeat-until
        self.semantic_stack.append(self.PC)

        self.num_open_repeats += 1

    def until(self, token):
        # jump back to label if condition is true
        # also check if there were any break statements before
        self.num_open_repeats -= 1
        temp_until_condition = self.semantic_stack.pop()  # the value that until should decide to jump based on it
        # check breaks
        while len(self.semantic_stack) > 0 and self.semantic_stack[-1] == "break":
            self.program_block_modification(self.semantic_stack[-2], operation="JP", first_op=self.PC + 1)
            self.pop_last_n(2)
        # jump back
        self.program_block_insert(operation="JPF", first_op=temp_until_condition,
                                  second_op=self.semantic_stack[-1])
        self.pop_last_n(1)

    def array_calc(self, token):
        # calculate the address of the index of the array
        # the index is on top of the stack and the address of array is the second element
        # pop those two and push the address of calculated address to the stack
        array_address = self.semantic_stack[-2]
        array_index = self.semantic_stack[-1]
        self.pop_last_n(2)

        array_type, _ = self.get_operand_type(array_address)
        temp = self.heap_manager.get_temp(array_type)
        self.program_block_insert(
            operation="*",
            first_op=array_index,
            second_op="#" + str(self.heap_manager.get_length_by_type(array_type)),
            third_op=temp
        )
        self.program_block_insert(
            operation="+",
            first_op=array_address,
            second_op=temp,
            third_op=temp
        )
        self.semantic_stack.append(str('@' + str(temp)))

    def push_op(self, token):
        # push operator to stack
        self.semantic_stack.append(token)

    def do_op(self, token):
        # do the operation
        # pop the operator and operands from the stack
        # push the result to the stack
        op = self.semantic_stack[-2]
        first_op = self.semantic_stack[-3]
        second_op = self.semantic_stack[-1]
        self.pop_last_n(3)
        # semantic: check operands types
        operands_type, is_array1 = self.get_operand_type(first_op)
        _, is_array2 = self.get_operand_type(second_op)
        if is_array1 or is_array2:
            self.semantic_analyzer.raise_semantic_error(line_no=self.current_line,
                                                        error=self.error_type_missmatch,
                                                        first_op="array",
                                                        second_op="int")
        temp = self.heap_manager.get_temp(operands_type)
        self.program_block_insert(operation=op, first_op=first_op, second_op=second_op, third_op=temp)
        self.semantic_stack.append(temp)

    def jpf_save(self, token):
        # jpf
        index_before_break = -1
        # remove breaks
        while self.semantic_stack[index_before_break] == "break":
            index_before_break -= 2
        breaks = []
        if index_before_break != -1:
            breaks = self.semantic_stack[index_before_break + 1:]
            self.semantic_stack = self.semantic_stack[:index_before_break + 1]

        self.program_block_modification(
            index=self.semantic_stack[-1],
            operation="JPF",
            first_op=self.semantic_stack[-2],
            second_op=str(self.PC + 1)
        )
        self.pop_last_n(2)
        # then save current pc
        self.semantic_stack.append(self.PC)
        self.program_block_insert_empty()
        # add back breaks
        self.semantic_stack.extend(breaks)

    def save(self, toke):
        # save the current PC
        self.semantic_stack.append(self.PC)
        self.program_block_insert_empty()

    def jp(self, token):
        # jump to a label

        index_before_break = -1
        while self.semantic_stack[index_before_break] == "break":
            index_before_break -= 2
        breaks = []
        # remove breaks
        if index_before_break != -1:
            breaks = self.semantic_stack[index_before_break + 1:]
            self.semantic_stack = self.semantic_stack[:index_before_break + 1]

        self.program_block_modification(
            index=self.semantic_stack[-1],
            operation="JP",
            first_op=str(self.PC)
        )
        self.pop_last_n(1)

        # add back breaks
        self.semantic_stack.extend(breaks)

    def id(self, token):
        # push the address of current token
        row = self.symbol_table.lookup(token, self.start_scope)
        if row is None:
            self.semantic_analyzer.raise_semantic_error(line_no=self.current_line,
                                                        error=self.error_scoping,
                                                        first_op=token)
            # add a dummy address of type int
            self.semantic_stack.append(self.heap_manager.get_temp("int", 1))

        else:
            address = row[address_key]
            self.semantic_stack.append(address)

    def push_eq(self, token):
        # in case of assignment, push = to stack
        # used for finding out if there is a nested assignment
        self.semantic_stack.append("=")

    def get_operand_type(self, operand):
        is_array = False
        if str(operand).startswith("#"):
            return "int", is_array
        elif str(operand).startswith("@"):
            operand = operand[1:]
        type = self.heap_manager.get_type_by_address(int(operand))
        if type.endswith("-arr"):
            type = type[:-4]
            is_array = True

        return type, is_array

    def print_pb(self):
        print("\n--------------Program Block---------------")
        for row in self.PB:
            print(row)

    def write_pb_to_file(self, output_file, semantic_file):
        if self.semantic_analyzer.num_semantic_errors > 0:
            output_file.write("The output code has not been generated.")
            for error in self.semantic_analyzer.all_errors:
                semantic_file.write(error + "\n")

            return

        for row in self.PB:
            output_file.write(str(row) + "\n")

    def push_function(self, token):
        # push function row index to stack (it's the last row of symbol table)
        self.FS.append(self.symbol_table.get_last_row_index())

    def pop_function(self, token):
        # pop function row index from stack
        self.FS.pop()

    def set_function_info(self, token):
        function_row_index = self.FS[-1]
        row = self.symbol_table.get_row_by_id(function_row_index)
        current_pc = self.PC
        return_address_temp = self.heap_manager.get_temp('int')
        return_value_temp = self.heap_manager.get_temp(row[type_key])
        self.symbol_table.modify_func_row_information(
            row_index=function_row_index,
            invocation_address=current_pc,
            return_address=return_address_temp,
            return_value=return_value_temp
        )

    def jump_out(self, token):
        # after the declaration of function is done,
        # we save a space in PB to tell us to jump out  of it and go to the declaration of next functions
        # Right now we know the next function. So we can fill out the saved row of PB
        self.program_block_modification(
            index=self.semantic_stack.pop(),
            operation="JP",
            first_op=str(self.PC)
        )

    def call_main(self, token):
        main_function_row = self.symbol_table.lookup("main")
        # set up the return address register of main
        self.program_block_insert(
            operation=":=",
            first_op="#" + str(self.PC + 2),
            second_op=str(main_function_row[return_address_key])
        )
        # now jump to the invocation address of main
        self.program_block_insert(
            operation="JP",
            first_op=str(main_function_row[invocation_address_key])
        )

    def show_scope_start(self, token):
        self.semantic_stack.append("scope_start")

    def pop_scope(self, token):
        breaks_array = []
        while self.semantic_stack[-1] != "scope_start":
            if self.semantic_stack[-1] == "break":
                breaks_array.append(self.semantic_stack.pop())
                breaks_array.append(self.semantic_stack.pop())
            else:
                self.semantic_stack.pop()
        self.semantic_stack.pop()
        breaks_array.reverse()
        self.semantic_stack.extend(breaks_array)
