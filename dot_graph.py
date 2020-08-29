import re
from operate_dot import OperateDot


class DFG:
    def __init__(self, path: str):
        self.line_list = []
        with open(path, 'r') as f:
            for line in f.readlines():
                if '->' in line:
                    self.line_list.append(line.strip())
        self.list2OPdot()


    def resolve_line(self, line: str):
        ''' line to dot '''
        res = re.findall(r'[a-zA-Z0-9_]+', line)
        return OperateDot(res[0]), OperateDot(res[1])


    def list2OPdot(self):
        self.dot_dict = {}
        for line in self.line_list:
            dot1, dot2 = self.resolve_line(line)
            
            if dot1.name in self.dot_dict:
                self.dot_dict[dot1.name].next.append(dot2.name)
            else:
                dot1.next.append(dot2.name)
                self.dot_dict[dot1.name] = dot1

            if dot2.name in self.dot_dict:
                self.dot_dict[dot2.name].pre.append(dot1.name)
            else:
                dot2.pre.append(dot1.name)
                self.dot_dict[dot2.name] = dot2

    def calculate_II(self, first_dot_name: str):
        pass

