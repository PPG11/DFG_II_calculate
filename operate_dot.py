import re
from operate_dot import OperateDot

def outputCheck(t: str, s:str) -> int:
    if t == 'LR':
        return 1
    elif t == 'GR':
        return 2
    else:
        raise Exception(f"输入有误! {s} 中第二参数非LR/GR")


class OperateDot:

    def __init__(self, s: str):
        '''
           s: input name string, eg: add1_GR_a2
        next: next dot name
         pre: previous dot name
        '''
        self.next = []
        self.pre = []
        line = s.split('_')
        n = len(line)
        if n == 1:
            self.name = line[0]
            self.output = 0
        elif n == 2:
            self.name = line[0]
            self.output = outputCheck(line[1], s)
        elif n == 3:
            self.name = line[0]
            self.output = outputCheck(line[1], s)
            self.schedule(line[2])
        else:
            raise Exception(f"输入有误! {s} 参数个数异常")
        self.decode_operation()
        
    

    def decode_operation(self):
        operation_latency = {
            'add': 1,
            'mul': 3,
            'load': 8
        }
        self.operation = re.search(r'[a-zA-Z]+', self.name)[0].lower()
        self.latency = operation_latency[self.operation]

    
    def schedule(self, schedule_str: str):
        self.schedule_class = re.search(r'[a-zA-Z]+', schedule_str)[0]
        self.schedule_idx = int(re.search(r'[0-9]+', schedule_str)[0])
