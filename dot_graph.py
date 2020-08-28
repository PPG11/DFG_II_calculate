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
        res = re.findall(r'[a-zA-Z0-9_]+', line)
        return res[0], res[1]


    def list2OPdot(self):
        self.name_list = []
        self.dot_list = []
        for line in self.line_list:
            dot1_str, dot2_str = self.resolve_line(line)
            dot1 = OperateDot(dot1_str)
            dot2 = OperateDot(dot2_str)
            
            if dot1.name in self.name_list:
                idx = self.name_list.index(dot1.name)
                self.dot_list[idx].next.append(dot2.name)
            else:
                dot1.next.append(dot2.name)
                self.dot_list.append(dot1)
                self.name_list.append(dot1.name)

        if dot2.name in self.name_list:
            idx = self.name_list.index(dot2.name)
            self.dot_list[idx].pre.append(dot1.name)
        else:
            dot2.pre.append(dot1.name)
            self.dot_list.append(dot2)
            self.name_list.append(dot2.name)

    def calculate_II(self):
        pass

