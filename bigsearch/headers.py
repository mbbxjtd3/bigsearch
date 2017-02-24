def find_headers(to_open, pattern_, f_out_name):

	f = open(to_open, 'r')
	f_out = open(f_out_name, "w")

	line = 1
	while line <>"":
		line = f.readline()

		if line.find(pattern_) <> -1:
			f_out.write(line)

	f.close()
	f_out.close()


