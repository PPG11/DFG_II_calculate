import re
from queue import Queue

from operate_dot import OperateDot

from typing import List, Tuple


class DFG:

    def __init__(self, path: str, iter_idle: int=0):
        self.path = path
        self.line_list = []
        self.iter_idle = iter_idle
        self.schedule_dict = {}
        with open(path, 'r') as f:
            self.title = f.readline()
            for line in f.readlines():
                if '->' in line:
                    self.line_list.append(line.strip())
        self.list2OPdot()


    def resolve_line(self, line: str) -> Tuple[OperateDot, OperateDot]:
        ''' line to dot '''
        res = re.findall(r'[a-zA-Z0-9_]+', line)
        return OperateDot(res[0], self.iter_idle), OperateDot(res[1], self.iter_idle)


    def list2OPdot(self):
        self.dot_dict = {}
        for line in self.line_list:
            dot1, dot2 = self.resolve_line(line)
            
            if dot1.name in self.dot_dict:
                self.dot_dict[dot1.name].succ.append(dot2.name)
            else:
                dot1.succ.append(dot2.name)
                self.dot_dict[dot1.name] = dot1

            if dot2.name in self.dot_dict:
                self.dot_dict[dot2.name].pre.append(dot1.name)
            else:
                dot2.pre.append(dot1.name)
                self.dot_dict[dot2.name] = dot2


    def eliminate_negative(self):
        min_initial_idle = 1
        for dot in self.dot_dict.values():
            if dot.initial_idle < min_initial_idle:
                min_initial_idle = dot.initial_idle
        
        if min_initial_idle < 1:
            diff = 1 - min_initial_idle
            for dot in self.dot_dict.values():
                dot.initial_idle += diff


    def calculate_II(self, first_dot_name: str):
        ''' KEY algorithm
            self.dot_dict: DFG describe dict
        '''
        q = Queue(maxsize=len(self.dot_dict))
        q.put(first_dot_name)
        first_dot = self.dot_dict[first_dot_name]
        first_dot.initial_idle = 1
        if first_dot.is_schedule_dot:
            self.schedule_dict[first_dot.schedule_class] = (1 - first_dot.schedule_idx) % (self.iter_idle + 1)
        
        while (not q.empty()):
            
            this_name = q.get()
            this_dot: OperateDot = self.dot_dict[this_name]
            # print(f'{this_dot.name}: {this_dot.initial_idle}')
            
            # succ dot
            succ_initial_idle = this_dot.succ_initial_idle()
            for name in this_dot.succ:
                dot: OperateDot = self.dot_dict[name]
                if dot.initial_idle == None:
                    # new dot
                    print(f'name:{dot.name} - II:{succ_initial_idle}')
                    dot.initial_idle = succ_initial_idle
                    if dot.is_schedule_dot:
                        if dot.schedule_class not in self.schedule_dict:
                            self.schedule_dict[dot.schedule_class] = (dot.initial_idle - dot.schedule_idx) % (self.iter_idle + 1)
                        else:
                            dot.schedule_offset = self.schedule_dict[dot.schedule_class]
                            dot.adjust_initial_idle()
                    q.put(dot.name)

            # pre dot
            for name in this_dot.pre:
                dot: OperateDot = self.dot_dict[name]
                if dot.initial_idle == None:
                    # new dot
                    dot.calculate_initial_idle_by_succ(this_dot.initial_idle, self.schedule_dict)
                    q.put(dot.name)
            
        # eliminate the negative initial idle
        self.eliminate_negative()

    def print_new_graph(self):
        for dot in self.dot_dict.values():
            dot.build_new_name()

        path = f'{self.path[:-4]}_II.dot'
        
        with open(path, 'w+', encoding='utf-8') as f:
            # first line
            f.write(f'{self.title}')
            # middle
            for dot in self.dot_dict.values():
                for succ_dot_name in dot.succ:
                    f.write(f'    {dot.new_name} -> {self.dot_dict[succ_dot_name].new_name}\n')
            # last line
            f.write('}')
            
