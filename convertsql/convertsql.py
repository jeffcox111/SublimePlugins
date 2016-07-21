import sublime, sublime_plugin, re

class convertsqlCommand(sublime_plugin.TextCommand):

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
		#content = content.replace('Trim(', 'rtrim(ltrim(')
		content = re.sub('trim\(([^\)]*)\)', self.createTrim, content);


		self.view.replace(edit, region, content)

	def createTrim(sender, matchobj):
			return 'rtrim(ltrim(' + matchobj.group(1) + '))'