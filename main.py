from dot_graph import DFG

path = './fft.dot'

d = DFG(path, iter_idle=4)
d.calculate_II('load11')
d.print_new_graph()