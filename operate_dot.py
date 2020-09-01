import re

from typing import List, Tuple, Dict


def outputCheck(t: str, s:str) -> int:
    t = t.upper()
    if t == 'NR':
        return 0
    elif t == 'LR':
        return 1
    elif t == 'GR':
        return 2
    else:
        raise Exception(f"输入有误! {s} 中第二参数非LR/GR/NR")


class OperateDot:

    def __init__(self, s: str, iter_idle: int=0):
        '''
           s: input name string, eg: add1_GR_a2
        '''
        self.succ: List[str] = []
        self.pre: List[str] = []
        self.iter_idle = iter_idle
        self.iter_group = iter_idle + 1
        self.class_offset = 0
        self.initial_idle: int = None
        self.need_adjust: bool = False
        self.is_schedule_dot = False
        line = s.split('_')
        n = len(line)
        if n == 1:
            self.name = line[0]
            self.output = 0
        elif n == 2:
            self.name = line[0]
            self.output = outputCheck(line[1], s)
        elif n == 3:
            self.need_adjust = True
            self.name = line[0]
            self.output = outputCheck(line[1], s)
            self.is_schedule_dot = True
            self.schedule(line[2])
        else:
            raise Exception(f"输入有误! {s} 参数个数异常")
        self.old_str = s
        self.decode_operation()
    

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

    
    def schedule(self, schedule_str: str):
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
        # print(f'{self.name}: ii-{self.initial_idle} latency-{self.latency} output-{self.output} iter-idle-{self.iter_group}')
        return self.initial_idle + self.latency + self.output + self.iter_group # - 1 + 1

    
    def calculate_initial_idle_by_succ(self, succ_initial_idle: int, schedule_class_dict: Dict[str, int]):
        self.initial_idle = succ_initial_idle - self.latency - self.output - self.iter_group # + 1 - 1
        if self.is_schedule_dot:
            if self.schedule_class not in schedule_class_dict:
                schedule_class_dict[self.schedule_class] = (self.initial_idle - self.schedule_idx) % self.iter_group
            else:
                self.schedule_offset = schedule_class_dict[self.schedule_class]
                self.adjust_initial_idle()
                if self.be_adjust:
                    self.initial_idle = self.initial_idle + self.iter_group

    
    def build_new_name(self):
        self.new_name = f'{self.old_str}_{self.initial_idle}'
