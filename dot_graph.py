import re
from operate_dot import OperateDot


class A:
    pass


def resolve_line(line: str):
    res = re.findall(r'[a-zA-Z0-9_]+', line)
    return res[0], res[1]


def dot2list(path: str):
    line_list = []
    with open(path, 'r') as f:
        for line in f.readlines():
            if '->' in line:
                line = line.strip()
                line_list.append(line)
    return line_list

def list2OPdot(line_list):
    name_list = []
    dot_list = []
    for line in line_list:
        dot1_str, dot2_str = resolve_line(line)
        dot1 = OperateDot(dot1_str)
        dot2 = OperateDot(dot2_str)
        
        if dot1.name in name_list:
            idx = name_list.index(dot1.name)
            dot_list[idx].next.append(dot2.name)
        else:
            dot1.next.append(dot2.name)
            dot_list.append(dot1)
            name_list.append(dot1.name)

        if dot2.name in name_list:
            idx = name_list.index(dot2.name)
            dot_list[idx].pre.append(dot1.name)
        else:
            dot2.pre.append(dot1.name)
            dot_list.append(dot2)
            name_list.append(dot2.name)

