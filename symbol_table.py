from heap_manager import HeapManager

class SymbolTable:

    def __init__(self, heap_manager) -> None:
        # row properties are id, lexeme, proc/func/var/param (kind), No. Arg/Cell (attributes), type, scope, address
        self.address_to_row = {}
        self.table = []
        self.current_scope = 0
        self.heap_manager = heap_manager
        self.scope_stack = [0]
        self.insert("output")
        self.modify_last_row("func", "void")
        self.table[-1]['attributes'] = 1
        self.table.append({'id': 1, 'lexeme': 'somethingwild', 'kind': "param", 'attributes': '-', 'type': "int",
                           'scope': 1, 'address': self.heap_manager.get_temp("int", 1)})

    def insert(self, lexeme):
        self.table.append({'id': len(self.table), 'lexeme': lexeme})

    def modify_last_row(self, kind, type):
        # after declaration of a variable by scanner, code generator needs
        # to complete the declaration by modifying the last row of symbol table
        self.table[-1]['kind'] = kind
        self.table[-1]['type'] = type
        self.table[-1]['address'] = self.heap_manager.get_temp(type, 1)
        self.table[-1]['scope'] = self.current_scope
        self.table[-1]['attributes'] = '-'
        self.address_to_row[self.table[-1]['address']] = len(self.table) - 1

    def modify_func_row_information(self, row_index, invocation_address, return_address, return_value):
        # add a "invocation_address" field to the row,
        # this is used when we declare a function and we want to invoke it. We should know where to jump to
        self.table[row_index]['invocation_address'] = invocation_address
        # add a "return_address" field to the row,
        # anyone who calls the function should put its address (PC) in this address
        self.table[row_index]['return_address'] = return_address
        # return value is the address of a temp that is supposed to hold the return value of the function
        self.table[row_index]['return_value'] = return_value

    def modify_attributes_last_row(self, num_attributes):
        # used for array declaration and function declaration
        # if arr_func == True then it is an array
        # else it is a function
        # note: for now it is only used for array declaration
        self.table[-1]['attributes'] = num_attributes

    def modify_attributes_row(self, row_id, num_attributes, arr_func: bool = True):
        # used for modifying function No. of args after counting them
        # if arr_func == True then it is an array
        # else it is a function
        self.table[row_id]['attributes'] = num_attributes

    def modify_kind_last_row(self, kind):
        self.table[-1]['kind'] = kind

    def add_scope(self):
        self.current_scope += 1
        self.scope_stack.append(len(self.table))

    def end_scope(self):
        # remove all rows of symbol table that are in the current scope
        # and update the current scope
        # remember function is first added and then the scope is added
        # also param type of the function that the scope is created for,
        # must not be removed
        remove_from = len(self.table)
        for i in range(self.scope_stack[-1], len(self.table)):
            if self.is_useless_row(i) or self.table[i]['kind'] != "param":
                remove_from = i
                break

        self.table = self.table[:remove_from]

        self.current_scope -= 1
        self.scope_stack.pop()

    def declare_array(self, num_of_cells):
        self.table[-1]['attributes'] = num_of_cells

    def lookup(self, name, start_ind=0, in_declare=False, end_ind=-1) -> dict:
        # search in symbol table
        # search for it between the start_ind and end_ind of symbol table
        # if end_ind == -1 then it means to search till the end of symbol table

        row_answer = None
        nearest_scope = -1
        end = end_ind

        if end_ind == -1:
            end = len(self.table)
            if in_declare and self.is_useless_row(-1):
                end -= 1

        while len(self.scope_stack) >= -nearest_scope:
            start = self.scope_stack[nearest_scope]

            for i in range(start, end):
                row_i = self.table[i]
                if not self.is_useless_row(i):
                    if nearest_scope != -1 and row_i['kind'] == "param":
                        pass
                    elif row_i['lexeme'] == name:
                        return row_i

            nearest_scope -= 1
            end = start

        return row_answer

    def remove_last_row(self):
        self.table.pop()

    def is_useless_row(self, id):
        if "type" not in self.get_row_by_id(id):
            return True

    def get_row_id_by_address(self, address) -> int:
        return self.address_to_row[address]

    def get_row_by_id(self, id) -> dict:
        return self.table[id]

    def get_id_last_row(self):
        return len(self.table) - 1

    def get_row_by_address(self, address) -> dict:
        return self.get_row_by_id(self.get_row_id_by_address(address))

    def get_last_row(self):
        return self.get_row_by_id(-1)

    def get_last_row_index(self):
        return len(self.table) - 1