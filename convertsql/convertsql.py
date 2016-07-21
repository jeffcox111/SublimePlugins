import sublime, sublime_plugin, re

class convertsqlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		content = self.view.substr(region)
		content = content.replace('!', '.')
		content = content.replace('&', '+')
		content = content.replace('"', '\'')
		#content = content.replace('dbo_', 'dbo.')

		# Replace DATE() with GETDATE()
		content = re.sub('\WDATE\w*\(\w*\)', ' GETDATE()', content)

		# Replace trim with rtrim + ltrim
		content = re.sub('\Wtrim\(([^\)]*)\)', self.createTrim, content);

		# Remove INTO clauses
		content = re.sub('(SELECT.*)(INTO\s*\S*)', r'\1', content)

		# Continue looping if we replace anything- there might be more nested inside.
		self.runConvertAgain = True
		while self.runConvertAgain is True:
			self.runConvertAgain = False
			# Replace IIf with CASE WHEN
			content = re.sub('\Wiif\w*\(([^,]*),([^,]*),([^\)]*)\)', self.createCaseWhen, content)

		# User can specify temp table name to INSERT INTO
		#self.view.window().show_input_panel("Destination temp table name: ", "#TempTable", self.setTempTableName, None, None)


		self.view.replace(edit, region, content)

		print("done")

	#def setTempTableName(self, temptablename):
	#	return

	def createTrim(self, matchobj):
		self.runConvertAgain = True
		print("converted trim")
		return ' rtrim(ltrim(' + matchobj.group(1) + '))'

	def createCaseWhen(self, matchobj):
		self.runConvertAgain = True
		return ' CASE WHEN ' + matchobj.group(1) + ' THEN ' + matchobj.group(2) + ' ELSE ' + matchobj.group(3)