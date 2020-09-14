import re

from typing import List, Tuple, Dict


def outputCheck(t: str, s:str) -> int:
    t = t.upper()[:2]
    if t == 'NR':
        return 0
    elif t == 'LR':
        return 1
    elif t == 'GR':
        return 2
    else:
        raise Exception(f"输入有误! {s} 中第二参数非LR/GR/NR")


class OperateDot:
    ''' is_edge_type = True  : load1_GR_a0
                     = False : load1 [out1=GR1, addr=1024, IItype=True]
    '''

    def __init__(self, s: str, iter_idle: int=0, is_edge_type: bool=True):
        ''' s: input name string, eg: add1_GR_a2
        '''
        self.succ: List[str] = []
        self.pre: List[str] = []
        self.iter_idle = iter_idle
        self.iter_group = iter_idle + 1
        self.class_offset = 0
        self.initial_idle: int = None
        self.need_adjust: bool = False
        self.is_schedule_dot = False
        self.schedule: str = None
        self.out1 = 'NR'
        self.is_edge_type = is_edge_type

        if is_edge_type:
            self.resolve_edge_type(s)
            self.old_node_name = s
        else:
            self.resolve_node_type(s)
            self.old_node_name = self.name
            
        self.decode_operation()


    def resolve_edge_type(self, s: str):
        ' load1_GR_a0 '
        line = s.split('_')
        n = len(line)
        if n == 1:
            self.name = line[0]
        elif n == 2:
            self.name = line[0]
            self.out1 = line[1]
        elif n == 3:
            self.need_adjust = True
            self.name = line[0]
            self.out1 = line[1]
            self.is_schedule_dot = True
            self.handle_schedule(line[2])
        else:
            raise Exception(f"输入有误! {s} 参数个数异常")
        self.output_latency = outputCheck(self.out1, s)


    def resolve_node_type(self, s: str):
        ' load1 [out1=GR1, addr=1024, IItype=True, schedule=a3] '
        # get name
        name_end_idx = s.find('[')
        self.name = s[:name_end_idx].strip()

        # get attr
        attr_str = s[name_end_idx+1:-1].replace(' ', '')
        attr_assign = attr_str.split(',')
        for line in attr_assign:
            attr, value = line.split('=')
            setattr(self, attr, value)

        self.output_latency = outputCheck(self.out1, s)
        if self.schedule != None:
            self.is_schedule_dot = True
            self.handle_schedule(self.schedule)


    def decode_operation(self):
        operation_latency = {
            'nop': 1,
            'route': 1,
            'add': 1,
            'sub': 1,
            'uadd': 1,
            'usub': 1,
            'and': 1,
            'or': 1,
            'xor': 1,
            'not': 1,
            'sel': 1,
            'shl': 1,
            'shr': 1,
            'arl': 1,
            'all': 1,
            'clz': 1,
            'mul': 3,
            'mac': 3,
            'umul': 3,
            'umac': 3,
            'msr': 4,
            'umsr': 4,
            'equal': 1,

            'div': 18,
            'udiv': 18,
            
            'load': 6,
            'store': 2
        }
        self.operation = re.search(r'[a-zA-Z]+', self.name)[0].lower()
        self.latency = operation_latency[self.operation]


    def handle_schedule(self, schedule_str: str):
        self.schedule_class = re.search(r'[a-zA-Z]+', schedule_str)[0]
        self.schedule_idx = int(re.search(r'[0-9]+', schedule_str)[0])
        self.schedule_offset = -1


    def adjust_initial_idle(self):
        ''' adjust the initial idle by `schedule_offset`, `schedule_idx` and `iter_group`
        '''
        now_idx = (self.initial_idle - self.schedule_offset) % self.iter_group
        diff = (now_idx - self.schedule_idx) 
        diff = diff if diff >= 0 else (diff + self.iter_group)
        self.initial_idle = self.initial_idle - diff
        self.be_adjust = True if diff != 0 else False

    
    def succ_initial_idle(self) -> int:
        ''' calculate the successor initial idle
            ! this idle is the original II of the successor
            ! for each dot, we need to adjust it by `schedule_class` and `schedule_idx`
        '''
        # print(f'{self.name}: ii-{self.initial_idle} latency-{self.latency} output_latency-{self.output_latency} iter-idle-{self.iter_group}')
        return self.initial_idle + self.latency + self.output_latency + self.iter_group # - 1 + 1

    
    def calculate_initial_idle_by_succ(self, succ_initial_idle: int, schedule_class_dict: Dict[str, int]):
        self.initial_idle = succ_initial_idle - self.latency - self.output_latency - self.iter_group # + 1 - 1
        if self.is_schedule_dot:
            if self.schedule_class not in schedule_class_dict:
                schedule_class_dict[self.schedule_class] = (self.initial_idle - self.schedule_idx) % self.iter_group
            else:
                self.schedule_offset = schedule_class_dict[self.schedule_class]
                self.adjust_initial_idle()
                if self.be_adjust:
                    self.initial_idle = self.initial_idle + self.iter_group

    
    def build_new_name(self):
        self.new_name = f'{self.old_node_name}_{self.initial_idle}'
