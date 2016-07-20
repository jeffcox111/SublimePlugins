import sublime, sublime_plugin

class convertsqlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		content = self.view.substr(region)
		content = content.replace('!', '.')
		content = content.replace('&', '+')
		self.view.replace(edit, region, content)
		
