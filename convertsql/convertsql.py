import sublime, sublime_plugin, re

class convertsqlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.edit = edit
		region = sublime.Region(0, self.view.size())
		content = self.view.substr(region)
		content = content.replace('!', '.')
		content = content.replace('&', '+')
		content = content.replace('"', '\'')
		content = content.replace('dbo_', '')

		# Replace DATE() with GETDATE()
		content = re.sub('([^a-z])DATE\w*\(\w*\)', r'\1GETDATE()', content)

		# Replace trim with rtrim + ltrim
		content = re.sub('([^a-z])Trim\(([^\)]*)\)', self.createTrim, content);

		# Remove INTO clauses
		content = re.sub('(SELECT.*)(INTO\s*\S*)', r'\1', content)

		# Continue looping if we replace anything- there might be more nested inside.
		self.runConvertAgain = True
		while self.runConvertAgain is True:
			# Replace IIf with CASE WHEN
			# Find IIf statement
			iifmatch = re.search('([^a-z])IIf\w*\(', content)
			if iifmatch is not None:
				content = self.convertIIf(content, iifmatch)
			else:
				self.runConvertAgain = False

		self.newSql = content

		# User can specify temp table name to INSERT INTO
		self.view.window().show_input_panel("Destination temp table name: ", "#TempTable", self.setTempTableName, None, None)

	def setTempTableName(self, temptablename):
		content = self.newSql

		if len(temptablename) > 0:
			# Temp table management
			content = 'IF OBJECT_ID(\'tempdb..' + temptablename + '\') IS NOT NULL DROP TABLE ' + temptablename + '\n' + content

			content = re.sub('(SELECT[\s\S]*)FROM', r'\1' + ' INTO ' + temptablename + ' FROM', content)

			content = content + '\nDROP TABLE ' + temptablename

		new_file = self.view.window().new_file()
		new_file.run_command('insert', {'characters': content})
		return

	def createTrim(self, matchobj):
		self.runConvertAgain = True
		return matchobj.group(1) + 'rtrim(ltrim(' + matchobj.group(2) + '))'

	def convertIIf(self, content, iifmatch):
		beforeIIf = content[:iifmatch.start(0)]

		condition = self.getIIfBlockStatement(content, iifmatch.end(0))
		trueresult = self.getIIfBlockStatement(content, iifmatch.end(0) + len(condition) + 1)
		falseresult = self.getIIfBlockStatement(content, iifmatch.end(0) + len(condition) + 1 + len(trueresult) + 1)

		afterIIf = content[iifmatch.end(0) + len(condition) + 1 + len(trueresult) + 1 + len(falseresult) + 1:]

		content = beforeIIf + ' CASE WHEN ' + condition + ' THEN ' + trueresult + ' ELSE ' + falseresult + ' END' + afterIIf
		
		return content

	def getIIfBlockStatement(self, content, startIndex):
		subContent = content[startIndex:]
		result = ''
		nestCounter = 0
		for c in subContent:
			if c is '(':
				nestCounter+=1
			if c is ')':
				nestCounter-=1
				if nestCounter is -1:
					break
			if c is ',':
				if nestCounter is 0:
					break
			result += c
		return result