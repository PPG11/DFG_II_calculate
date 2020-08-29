from dot_graph import DFG

path = './test.dot'

d = DFG(path)
d.calculate_II('load1')
d.print_new_graph()