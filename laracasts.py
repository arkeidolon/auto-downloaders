import sys
import os

download_path = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	'laracasts/'
)

def latest_episode(folder_name):
	episodes =  os.listdir(folder_name)
	latest_episode = 0

	for episode in episodes:
		episode_number = int(episode.split(' ')[0])
		if episode_number > latest_episode:
			latest_episode = episode_number

	return latest_episode

if len(sys.argv) < 2:
	print 'Incomplete number of args.'
	print 'Usage: python laracasts.py email_address [from_episode]'
else:
	import mechanize

	import urllib2
	import cookielib
	import cgi

	from getpass import getpass

	class NoHistory(object):
		def add(self, *a, **k): pass
		def clear(self): pass
		def close(self): pass

	def read_in_chunks(file_object):
		progress = 1
		while True:
			data = file_object.readline()
			if not data:
				break

			yield progress, data
			progress += 1

	cj = cookielib.CookieJar()
	br = mechanize.Browser(history=NoHistory())
	br.set_handle_robots(False)

	br.set_cookiejar(cj)
	br.open("https://laracasts.com/login")

	br.select_form(nr=0)
	br.form['email'] = sys.argv[1]
	br.form['password'] = getpass()
	br.submit()

	print 'Logging in...'
	response = br.response().read()

	if 'You are now logged in!' in response:
		print 'You are now logged in! Scraping...'

		download_url = "https://laracasts.com/downloads/%s?type=episode"

		i = int(sys.argv[2]) if len(sys.argv) > 2 else latest_episode(download_path)+1

		while True:
			video_link = download_url%i

			episode_number = '%04d'%i

			print 'Downloading from %s...'%video_link

			br.open(video_link)

			if br.viewing_html():
				print '%s does not exist.'%episode_number
			else:
				response = br.response()

				headers = response.info().headers

				_, params = cgi.parse_header(
					[
						header for header in headers
							if 'Content-Disposition' in header
					][0])

				bytes_count = [
					header for header in headers
						if 'Content-Length' in header
				][0]

				print bytes_count

				title = params['filename']
				body = '';

				for (progress, chunk) in read_in_chunks(response):
					print '\r%d'%progress,
					body += chunk

				filename = '%s %s'%(episode_number, title)

				print 'Saving...',

				f = open(os.path.join(download_path, filename), 'w')
				f.write(body)
				f.close()

				print '\rSaved to %s!'%filename

			i += 1
	else:
		print 'Failed to log in.'

	br.close()
