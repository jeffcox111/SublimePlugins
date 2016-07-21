import sublime, sublime_plugin, re

class convertsqlCommand(sublime_plugin.TextCommand):
	runConvertAgain = false

	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		content = self.view.substr(region)
		content = content.replace('!', '.')
		content = content.replace('&', '+')
		content = content.replace('"', '\'')
		content = content.replace('[', '')
		content = content.replace(']', '')
		content = content.replace('dbo_', 'dbo.')

		# Replace trim with rtrim + ltrim
		content = re.sub('\Wtrim\(([^\)]*)\)', self.createTrim, content);

		# Replace IIf with CASE WHEN
		content = re.sub('\Wiif\w*\(([^,]*),([^,]*),([^\)]*)\)', self.createCaseWhen, content)

		# Replace DATE() with GETDATE()
		content = re.sub('\WDATE\w*\(\w*\)', 'GETDATE()', content)

		self.view.replace(edit, region, content)

	def createTrim(self, matchobj):
		return 'rtrim(ltrim(' + matchobj.group(1) + '))'

	def createCaseWhen(self, matchobj):
		return 'CASE WHEN ' + matchobj.group(1) + ' THEN ' + matchobj.group(2) + ' ELSE ' + matchobj.group(3)