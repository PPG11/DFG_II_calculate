import re
from queue import Queue

from operate_dot import OperateDot

from typing import List, Tuple


class DFG:
    ''' file (test.dot)
        |
        | -- [init]
        V
        list ('load1_GR_a0 -> add1_NR')
        |
        | -- [edge_list2OPdot : resolve_edge_line]
        V
        OperateDot (dot_dict： {'load1': OPDot})
    '''

    def __init__(self, path: str, iter_idle: int=0, is_edge_type: bool=True):
        self.path = path
        # self.line_list = []
        self.iter_idle = iter_idle
        self.schedule_dict = {}
        self.dot_dict = {}
        self.is_edge_type = is_edge_type
        if is_edge_type:
            self.resolve_edge_type(path)
        else:
            self.resolve_node_type(path)

    
    def resolve_node_type(self, path: str):
        ''' 0. load file & get `title`
            1. build (dot1 dot2), 
            2. put (dot1 dot2) into `dot_dict`
            3. build edge (dot1 -> dot2)
        '''
        with open(path, 'r') as f:
            node_str_list = []
            edge_str_list = []
            self.title = f.readline()
            for line in f.readlines():
                if '[' in line:
                    node_str_list.append(line.strip())
                elif '->' in line:
                    edge_str_list.append(line.strip())
            self.node_str_list = node_str_list
        self.node_and_edge_2_OPdot(node_str_list, edge_str_list)

    
    def node_and_edge_2_OPdot(self, node_str_list: List[str], edge_str_list: List[str]):
        # 1. build (dot)
        # 2. put (dot) into `dot_dict`
        for line in node_str_list:
            dot = OperateDot(line, self.iter_idle, is_edge_type=False)
            self.dot_dict[dot.name] = dot

        # 3. build edge (dot1 -> dot2)
        for line in edge_str_list:
            res = re.findall(r'[a-zA-Z0-9_]+', line)
            dot1, dot2 = self.dot_dict[res[0]], self.dot_dict[res[1]]
            self.build_edge(dot1, dot2)

    
    def resolve_edge_type(self, path: str):
        ''' 0. load file & get `title`
            1. build (dot1 dot2), 
            2. put (dot1 dot2) into `dot_dict`
            3. build edge (dot1 -> dot2)
        '''
        with open(path, 'r') as f:
            line_list = []
            self.title = f.readline()
            for line in f.readlines():
                if '->' in line:
                    line_list.append(line.strip())
        self.edge_list2OPdot(line_list)


    def resolve_edge_line(self, line: str) -> Tuple[OperateDot, OperateDot]:
        ''' line to dot '''
        res = re.findall(r'[a-zA-Z0-9_]+', line)
        return OperateDot(res[0], self.iter_idle), OperateDot(res[1], self.iter_idle)


    def edge_list2OPdot(self, line_list: List[str]):
        for line in line_list:
            dot1, dot2 = self.resolve_edge_line(line)
            self.build_edge(dot1, dot2)


    def build_edge(self, dot1: OperateDot, dot2: OperateDot):
        ' dot1 -> dot2 '
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
                    # print(f'name:{dot.name} - II:{succ_initial_idle}')
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
            # 1. first line
            f.write(f'{self.title}')
            
            # 2. middle
            # 2.1 for node type, need to write node info
            if not self.is_edge_type:
                for line in self.node_str_list:
                    name_end_idx = line.find('[')
                    dot_name = line[:name_end_idx].strip()
                    dot = self.dot_dict[dot_name]
                    attr = line[name_end_idx+1:-1]

                    f.write(f'    {dot.new_name} [{attr}, II={dot.initial_idle}]\n')
                f.write('\n')

            # 2.2 both the (node & edge) type need to write edge info
            for dot in self.dot_dict.values():
                for succ_dot_name in dot.succ:
                    f.write(f'    {dot.new_name} -> {self.dot_dict[succ_dot_name].new_name}\n')
            
            # 3. last line
            f.write('}')
