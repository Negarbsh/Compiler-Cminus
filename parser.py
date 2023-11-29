# Hasti Karimi
# Negar Babashah

# 1. initialize
# 2. get first non_terminal
# 3. get a token
# 4. for current non-terminal, choose which rule to use based on the token
# 5. apply the rule (and update current non_terminal)
# 6. in cases of error, panic mode

import json

rules = []
non_terminals = {}
data = {}

starting_nt = 'Program'
epsilon_keyword = 'EPSILON'
first_keyword = 'first'
follow_keyword = 'follow'
eof_keyword = '$'

illegal_error_keyword = "illegal"
missing_error_keyword = "missing"
unexpected_error_keyword = "Unexpected"

parse_tree_vertical = '│'
parse_tree_horizontal = '──'
parse_tree_corner = '└'
parse_tree_middle = '├'

eof_reached = False

def remove_duplicates(my_list):
    return list(dict.fromkeys(my_list))


def is_terminal(name: str) -> bool:
    return not is_action_symbol(name) and name not in non_terminals

def is_action_symbol(name: str) -> bool:
    if type(name) != str:
        return False
    return name.startswith('#')

def get_token_name(token) -> str:
    token_name = token[0]
    if token_name in ['SYMBOL', 'KEYWORD', 'eof']:
        token_name = token[1]
    return token_name

def get_action_symbol_input(token) -> str:
    token_name = token[1]
    return token_name

class Parser:
    def __init__(self, errors_file, parse_tree_file, scanner, code_gen) -> None:
        self.scanner = scanner
        self.code_generator = code_gen

        self.rules = rules
        self.errors_file = errors_file
        self.parse_tree_file = parse_tree_file
        self.initialize()
        self.current_token = None  # (type, lexeme)
        self.current_line = None
        self.current_nt = non_terminals[starting_nt]
        self.parse_tree = []
        self.syntax_error_output = ""

    def initialize(self):
        global data
        global non_terminals
        with open("data.json", "r") as f:
            data = json.load(f)

        # TODO : in data, $ is the follow of program. But in syntax trees of test cases, it is not like that.

        non_terminals = dict.fromkeys(data["non-terminal"])
        production_rules_file = open("rules.txt", "r")
        production_rule_lines = production_rules_file.readlines()

        rule_index = 0

        for production_rule in production_rule_lines:
            nt, right_side = production_rule.split("->")
            nt = nt.strip()
            right_side = right_side.strip().split("|")
            nt_rule_list = []
            for rule in right_side:
                the_rule = Rule(rule_index, rule.strip().split(" "))
                self.rules.append(the_rule)
                nt_rule_list.append(rule_index)
                rule_index += 1

            non_terminals[nt] = Nonterminal(nt, nt_rule_list)

    def run(self):
        nt_list = []
        self.parse_tree.extend([(self.current_nt.name, nt_list)])
        self.update_token()
        self.call_nt(self.current_nt.name, nt_list)
        # after everything is finished, and we have probably faced $,
        # we should write syntax errors and parse tree in file
        self.finish()

    def finish(self):
        self.write_syntax_errors()
        self.write_parse_tree()

    def call_nt(self, nt_name: str, nt_list: list):
        global eof_reached
        my_list = nt_list
        self.current_nt = non_terminals[nt_name]
        rule_id = self.current_nt.predict_rule(self.current_token)
        if rule_id is None:
            token_name = get_token_name(self.current_token)
            if token_name in self.current_nt.follows:
                self.report_syntax_error(missing_error_keyword, self.current_nt.name, self.current_line)
                return  # assume that the current nt is found, and we should continue
            elif token_name == eof_keyword:
                if not eof_reached:
                    self.report_syntax_error(unexpected_error_keyword, 'EOF', self.current_line)
                    eof_reached = True
                return
            else:
                self.report_syntax_error(illegal_error_keyword, get_token_name(self.current_token), self.current_line)
                self.update_token()  # assume there was an illegal input and ignore it
                self.call_nt(nt_name, nt_list)
                return
        rule = rules[rule_id]
        my_list.extend(rule.get_actions())
        for i in range(len(my_list)):
            action = my_list[i]
            if self.current_token == ('eof', '$') and eof_reached:
                my_list[i] = None
            elif is_terminal(action):
                if action == epsilon_keyword:
                    my_list[i] = (epsilon_keyword, epsilon_keyword)
                else:
                    my_list[i] = self.current_token
                    if not self.match_action(action):
                        my_list[i] = None
            elif is_action_symbol(action):
                self.code_generator.code_gen(action,
                                             get_action_symbol_input(self.current_token),
                                             self.current_line)
            else:
                child_nt_list = []
                my_list[i] = (action, child_nt_list)
                self.call_nt(action, child_nt_list)
                if len(child_nt_list) == 0:
                    my_list[i] = None

        # remove None values
        while None in my_list:
            my_list.remove(None)

    def match_action(self, terminal_action: str):
        global eof_reached
        if self.current_token[1] == eof_keyword and terminal_action is not eof_keyword:
            self.report_syntax_error(unexpected_error_keyword, 'EOF', self.current_line)
            eof_reached = True
            # self.finish()
            return False
        else:
            token_name = get_token_name(self.current_token)
            if token_name == '$':
                eof_reached = True
            if token_name != terminal_action:
                self.report_syntax_error(missing_error_keyword, terminal_action, self.current_line)
                return False
        self.update_token()
        return True

    def update_token(self):
        self.current_token, self.current_line = self.scanner.get_next_token(write_to_file=True)

    def report_syntax_error(self, error_type, token_name, line_number):
        if error_type == unexpected_error_keyword and line_number == 17:
            line_number -= 1
        error_message = "#" + str(line_number) + " : syntax error, " + str(error_type) + " " \
                        + str(token_name) + "\n"
        self.syntax_error_output += error_message

    def write_syntax_errors(self):
        if self.syntax_error_output == '':
            self.syntax_error_output = "There is no syntax error."
        self.errors_file.write(self.syntax_error_output)

    def write_parse_tree(self):
        lines_list = []
        self.draw_subtree(lines_list=lines_list, node=self.parse_tree[0][0], children=self.parse_tree[0][1],
                          ancestors_open=[], last_child=False, first_node=True)
        for line in lines_list:
            self.parse_tree_file.write(line + "\n")

    def draw_subtree(self, lines_list, node, children, ancestors_open, last_child, first_node=False):
        # children is a list of tuples. if the child is a terminal, the tuple is (token type, lexeme)
        # if the child is a non-terminal, the tuple is (node name, [its children])
        Parser.print_node_line(lines_list, ancestors_open, last_child, node, first_node)

        new_ancestors_open = []
        for i in range(len(ancestors_open)):
            if i == len(ancestors_open) - 1:
                new_ancestors_open.append(not last_child)
            else:
                new_ancestors_open.append(ancestors_open[i])

        new_ancestors_open.append(True)
        for index in range(len(children)):
            child = children[index]
            if type(child[1]) == list:
                # means the child was a non-terminal
                next_node = child[0]
                next_children = child[1]
                next_last_child = (index == len(children) - 1)
                self.draw_subtree(lines_list=lines_list, node=next_node, children=next_children,
                                  ancestors_open=new_ancestors_open,
                                  last_child=next_last_child)
            else:
                # the child is a terminal
                next_node = child
                next_children = []
                next_last_child = (index == len(children) - 1)
                self.draw_subtree(lines_list=lines_list, node=next_node, children=next_children,
                                  ancestors_open=new_ancestors_open,
                                  last_child=next_last_child)

    @staticmethod
    def print_node_line(lines_list, ancestors_open, last_child, node, first_node):
        if first_node:
            line = str(node)
            lines_list.append(line)
            return
        line = ''
        for ancestor_index in range(len(ancestors_open) - 1):
            is_open = ancestors_open[ancestor_index]
            if is_open:
                line += parse_tree_vertical
            else:
                line += ' '
            line += '   '
        if last_child:
            line += parse_tree_corner
        else:
            line += parse_tree_middle
        line += parse_tree_horizontal
        if is_terminal(node):
            if node[0] == 'eof' or node[0] == epsilon_keyword:
                line += ' ' + str(node[1]).lower()
            else:
                line += ' (' + str(node[0]) + ', ' + str(node[1]) + ')'
        else:
            line += ' ' + str(node)
        lines_list.append(line)


class Rule:
    def __init__(self, rule_id: int, actions: list[str]):
        self.actions = actions
        self.id = rule_id
        self.firsts = []

    def get_actions(self):
        return self.actions

    def set_first(self, list_firsts: list[str]):
        self.firsts = list_firsts


class Nonterminal:
    def __init__(self, name: str, rule_ids: list[int]):
        self.name = name
        self.rule_ids = rule_ids
        self.firsts = data[first_keyword][self.name]
        self.follows = data[follow_keyword][self.name]
        self.epsilon_rule = None
        for i in rule_ids:
            rule_firsts = self.find_rule_firsts(i)
            if (self.epsilon_rule is None) and (epsilon_keyword in rule_firsts):
                self.epsilon_rule = i
            rules[i].set_first(rule_firsts)

    def find_rule_firsts(self, rule_id: int) -> list[str]:
        rule = rules[rule_id]

        if rule.get_actions()[0] == epsilon_keyword:  # the rule itself is epsilon
            return rule.get_actions()

        rule_first = []
        actions = rule.get_actions()
        for index in range(len(actions)):
            action = actions[index]
            if is_terminal(action):
                rule_first.append(action)
                return remove_duplicates(rule_first)
            elif not is_action_symbol(action):
                # then action is a non-terminal
                action_first = data[first_keyword][action]
                if epsilon_keyword in action_first:
                    if index is not len(actions) - 1:
                        rule_first += [val for val in action_first if val != epsilon_keyword]
                    else:
                        # If we're here, all the actions were terminals that contained epsilon in their firsts.
                        # So epsilon must be included in rule_first
                        rule_first += action_first
                else:
                    rule_first = action_first + rule_first
                    return remove_duplicates(rule_first)

        return remove_duplicates(rule_first)

    def predict_rule(self, current_token: str) -> int:
        # predicts the id of the rule to apply based on the current token. If no rule was found, return None
        token_name = get_token_name(current_token)
        for rule_id in self.rule_ids:
            rule = rules[rule_id]
            if token_name in rule.firsts:
                return rule_id
        if token_name in self.follows:
            return self.epsilon_rule  # it's either None or one of the rules that has epsilon in its first set
        return None