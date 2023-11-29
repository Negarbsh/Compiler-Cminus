import string

class State:

    def __init__(self, id: int, terminality_status: int, type_id: int = 0, error_string: str = "Invalid input"):
        self.transitions = {}
        self.id = id
        self.error_str = error_string
        # terminality status:
        # 0: is none-terminal
        # 1: is terminal and non-star
        # 2: is terminal and with star
        self.terminality_status = terminality_status
        self.type_id = type_id

    def add_transition(self, char: str, goal_state: int):
        self.transitions[char] = goal_state

    def get_next_state(self, character: str) -> int:
        if character in self.transitions:
            return self.transitions[character]
        elif "all" in self.transitions and character != "$":
            return self.id
        return -1

    def get_error(self, character: str = "") -> str:
        return self.error_str

char_groups = [[";", ":", ",", "[", "]", "(", ")", "{", "}", "+", "-", "<"], ["*"], ["="], ["/"],
               ["\n", "\r", "\t", "\v", "\f", " "], ["$"], list(string.ascii_letters),
               ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], ["all"]]


def make_transition(chars_id: list[int], goal_states: list[int], state: State):
    if len(chars_id) != len(goal_states):
        print("basi wrong")

    for i in range(len(chars_id)):
        for char in char_groups[chars_id[i]]:
            state.add_transition(char, goal_states[i])


class Scanner:

    def __init__(self, input_file, output_file, lex_file, sym_file, symbol_table):
        self.input_file = input_file
        self.output_file = output_file
        self.lex_file = lex_file
        self.sym_file = sym_file
        self.symbol_table = symbol_table
        self.types = {1: "NUM", 2: "ID", 3: "KEYWORD", 4: "SYMBOL", 5: "COMMENT", 6: "WHITESPACE"}
        self.keywords = ["break", "else", "if", "int", "repeat", "return", "until", "void"]

        # elements of the symbol table - keywords should go first.
        self.identifiers = []
        self.sym_table_index = 0
        self.sym_table_initialized = False

        self.update_output_file_index = True

        self.line_number = 0
        self.current_line = ""
        self.is_eof_reached = False
        self.comment = ""
        self.comment_line = -1

        # when we have a token in substring [i, i+1, ..., j], start pointer should be i and end pointer should be j
        # if we want to read a character, we should read input[end pointer]
        self.start_pnt = 0
        self.end_pnt = -1
        self.errors = []

        self.state_list = []
        self.make_state_list(state_list=self.state_list)

    def make_state_list(self, state_list):
        s = State(id=0, terminality_status=0)
        make_transition(chars_id=[7, 5, 6, 0, 2, 3, 4, 1], goal_states=[1, 0, 3, 5, 6, 9, 16, 11],
                        state=s)

        state_list.append(s)

        s = State(id=1, terminality_status=0, error_string="Invalid number")
        make_transition(chars_id=[0, 1, 2, 3, 4, 5, 7], goal_states=[2, 2, 2, 2, 2, 2, 1],
                        state=s)

        state_list.append(s)

        s = State(id=2, terminality_status=2, type_id=1)
        state_list.append(s)

        s = State(id=3, terminality_status=0)
        make_transition(chars_id=[0, 1, 2, 3, 4, 5, 6, 7], goal_states=[4, 4, 4, 4, 4, 4, 3, 3],
                        state=s)
        state_list.append(s)

        s = State(id=4, terminality_status=2, type_id=2)
        state_list.append(s)

        s = State(id=5, terminality_status=1, type_id=4)
        state_list.append(s)

        s = State(id=6, terminality_status=0)
        make_transition(chars_id=[0, 1, 2, 3, 4, 6, 7], goal_states=[7, 7, 8, 7, 7, 7, 7],
                        state=s)
        state_list.append(s)

        s = State(id=7, terminality_status=2, type_id=4)
        state_list.append(s)

        s = State(id=8, terminality_status=1, type_id=4)
        state_list.append(s)

        s = State(id=9, terminality_status=0)
        make_transition(chars_id=[1, 0, 2, 3, 4, 5, 6, 7], goal_states=[13, 10, 10, 10, 10, 10, 10, 10],
                        state=s)
        state_list.append(s)

        s = State(id=10, terminality_status=2, type_id=4)
        state_list.append(s)

        s = State(id=11, terminality_status=0, error_string="Unmatched comment")
        make_transition(chars_id=[0, 1, 2, 4, 5, 6, 7], goal_states=[12, 12, 12, 12, 12, 12, 12],
                        state=s)
        state_list.append(s)

        s = State(id=12, terminality_status=2, type_id=4)
        state_list.append(s)

        s = State(id=13, terminality_status=0, error_string="Unclosed comment")
        make_transition(chars_id=[0, 1, 2, 3, 4, 6, 7, 8], goal_states=[13, 14, 13, 13, 13, 13, 13, 13],
                        state=s)
        state_list.append(s)

        s = State(id=14, terminality_status=0, error_string="Unclosed comment")
        make_transition(chars_id=[0, 1, 2, 3, 4, 6, 7], goal_states=[13, 14, 13, 15, 13, 13, 13],
                        state=s)
        state_list.append(s)

        s = State(id=15, terminality_status=1, type_id=5)
        state_list.append(s)

        s = State(id=16, terminality_status=1, type_id=6)
        state_list.append(s)

    # returns a tuple (next_char, line_updated)
    def get_next_char(self):
        line_updated = False
        if self.is_eof_reached:
            return '$', line_updated
        if self.line_number == 0 or self.end_pnt >= len(self.current_line) - 1:
            new_line = self.input_file.readline()
            if len(new_line) == 0:
                # end of file
                self.end_pnt += 1
                self.is_eof_reached = True
                return '$', line_updated
            self.current_line = new_line
            self.end_pnt = -1
            self.start_pnt = 0
            self.line_number += 1
            line_updated = True

        # if self.start_pnt == self.end_pnt:
        #     self.start_pnt = self.end_pnt + 1
        self.end_pnt += 1
        return self.current_line[self.end_pnt], line_updated

    # if a type (id, number,...) is valuable for parser, returns true, else false
    @staticmethod
    def is_type_parsable(type_id: int):
        return type_id not in [5, 6]

    # output:
    #   the next token valuable for parser
    #   None if no other token is available
    def get_next_token(self, write_to_file=True):
        self.comment_line = -1
        state_id = 0
        while self.state_list[state_id].terminality_status == 0:
            next_char, line_updated = self.get_next_char()

            if state_id == 13 and self.comment_line == -1 and self.end_pnt - self.start_pnt == 6:
                self.comment = self.current_line[self.start_pnt: self.end_pnt + 1]
                self.comment_line = self.line_number

            if line_updated:
                self.update_output_file_index = True
            # if next_char == "\n":
            #     pass
            next_state_id = self.state_list[state_id].get_next_state(next_char)
            if next_state_id == 10:
                next_state_id = -1
                state_id = 10
                self.end_pnt -= 1
            # the id of eof state is 0
            if next_state_id == 0:
                return ('eof', '$'), self.line_number + 1 # todo fine?
            if next_state_id == -1:
                self.handle_error(state_id, next_char)
                self.start_pnt = self.end_pnt + 1
                return self.get_next_token()

            state_id = next_state_id

        if self.state_list[state_id].terminality_status == 2:
            self.end_pnt -= 1

        lexeme = self.current_line[self.start_pnt: self.end_pnt + 1]
        type_id = self.state_list[state_id].type_id

        if type_id == 2:
            if lexeme in self.keywords:
                type_id = 3

        self.start_pnt = self.end_pnt + 1

        if Scanner.is_type_parsable(type_id):
            token = self.types[type_id], lexeme
            if write_to_file:
                self.write_sym_file(token)
                self.write_output_file(token)
            self.install_in_symbol_table(token)
            return token, self.line_number  # todo fine?
        else:
            return self.get_next_token()

    def handle_error(self, state_id: int, char: str):
        lexeme = self.current_line[self.start_pnt: self.end_pnt + 1]
        if state_id == 13 or state_id == 14:
            lexeme = self.comment
            self.errors.append([self.comment_line, lexeme + "...", self.state_list[state_id].get_error()])
            return
        if state_id == 11 and char != "/":
            self.errors.append([self.line_number, lexeme, "Invalid input"])
            return

        self.errors.append([self.line_number, lexeme, self.state_list[state_id].get_error()])
        # print("error!!!     " + self.state_list[state_id].get_error() + " the lexeme is " + lexeme)

    def install_in_symbol_table(self, token):
        id_type = "ID"
        type, lexeme = token
        if type == id_type:
            if lexeme not in self.identifiers:
                self.identifiers.append(lexeme)
                # if lexeme != "output":
                #     self.symbol_table.insert(lexeme)

    def write_sym_file(self, token):
        keyword_type = "KEYWORD"
        id_type = "ID"
        type, lexeme = token
        if type != keyword_type and type != id_type:
            return
        text = ""
        index_separator = ".\t"

        if not self.sym_table_initialized:
            for keyword in self.keywords:
                self.sym_table_index += 1
                text += str(self.sym_table_index) + index_separator + keyword + "\n"
                # we can omit it but it will make the program to not allow program default keywords redefinition.
            self.sym_table_initialized = True

        if type == id_type:
            if lexeme not in self.identifiers:
                self.sym_table_index += 1
                text += str(self.sym_table_index) + index_separator + lexeme + "\n"

        if len(text) != 0:
            self.sym_file.write(text)

    #   new_token: the token (type, lexeme) to add to output file
    #   line_updated: a bool that shows if the token is for a new line (we should update the line numbre in file)
    def write_output_file(self, new_token):
        type, lexeme = new_token
        text = ""
        if self.update_output_file_index:
            self.update_output_file_index = False
            if self.line_number != 1:
                text += "\n"
            text += str(self.line_number) + ".\t"
        else:
            text += " "
        text += "(" + type + ", " + lexeme + ")"
        self.output_file.write(text)

    def write_error_file(self):
        text = ""
        if len(self.errors) == 0:
            text = "There is no lexical error."
        else:
            index = 0
            while index < len(self.errors):
                line = self.errors[index][0]
                text += str(line) + ".\t(" + self.errors[index][1] + ", " + self.errors[index][2] + ") "
                index += 1
                while index < len(self.errors) and self.errors[index][0] == line:
                    text += "(" + self.errors[index][1] + ", " + self.errors[index][2] + ") "
                    index += 1

                text = text[:-1] + "\n"

        self.lex_file.write(text)
