def process(frame, segments, path):
	i = 0
	for segment in segments:
		import os, re, cv2, operator, codecs
		import HTMLParser
		parser = HTMLParser.HTMLParser()
		i += 1
		unit_indent = "   "

		image = segment
		output = path+"/frame%d-segment%d" % (frame, i)
		ocr_command = "tesseract " + image+output + " config.txt 2>/dev/null"
		os.system(ocr_command)

		# hocr output conversion
		res = [] # distance, code
		with open(output_path+"/frame%d-segment%d.hocr" % (frame, i)) as hocr_output:
			for line in hocr_output:
				# find x-coordinate of upper left corner
				location = re.search(r'(?<=bbox ).+?(?=\s)', line)

				# ignore tags and extract code
				text = re.sub(r'<[^>]*>', '', line)
				# fix special characters
				text = text.strip().decode("utf8")
				# dumb down smart quotes
				text = text.replace(u'\u201c', '"').replace(u'\u201d', '"')
				# decode HTML-safe sequences
				text = parser.unescape(text)

				# sanity check for location and extract
				is_text_empty = (text == re.search(r'\w*', line).group(0))
				if location != None and not is_text_empty:
					res.append([int(location.group(0)), text])

		# spacing adjustment

		if len(res) == 0:
			os.system("rm "+output_path+"/frame%d-segment%d.*" % (frame, i))

		else:
			os.system("rm "+output_path+"/frame%d-segment%d.hocr" % (frame, i))
			base = min(res, key=operator.itemgetter(0))[0]

			# yet to address case when 30,33,62 happens
			temp = [r for r in res if r[0] > base*1.09] # when base = 0
			if len(temp) == 0:
				lines = ""
				for r in res:
					lines += r[1] + "\n"

				# _dis[placed]
				f = codecs.open(output_path+"/frame%d-segment%d.txt" % (frame, i), 'w', 'utf-8') # _check.txt
				f.write(lines)

			else:
				tab = min(temp, key=operator.itemgetter(0))[0]-base

				res = [[int(round((r[0]-float(base))/tab)), r[1]] for r in res]
				indented_lines = ""
				for r in res:
					indented = ""
					for x in range(r[0]):
						indented += unit_indent
					indented += r[1]
					indented_lines += indented + "\n"

				# _ind[ented]
				f = codecs.open(output_path+"/frame%d-segment%d.txt" % (frame, i), 'w', 'utf-8')
				f.write(indented_lines)
