from dot_graph import DFG

# path = './fft.dot'

# d = DFG(path, iter_idle=4)
# d.calculate_II('load11')
# d.print_new_graph()


path = './test2.dot'

d = DFG(path, iter_idle=0, is_edge_type=False)
d.calculate_II('load1')
d.print_new_graph()