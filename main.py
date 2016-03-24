#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import cgi

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
	
#creates a datastore key with the 'Comment' and place_name as parameters, place_name used so comments about different places will be stored in different keys
def comment_key(place_name):
	return ndb.Key('Comment', place_name)
#a class to create Comment objects with the author, content and datetime properties
class Comment(ndb.Model):
	author = ndb.StringProperty(indexed=False) #need to find out what the indexed = False means
	content = ndb.StringProperty(indexed=False)
	datetime = ndb.DateTimeProperty(auto_now_add=True) #gets the current date and time
	
	
class MainHandler(webapp2.RequestHandler):
    def get(self):
	# for button that changes depending on whether user is logged in
		user = users.get_current_user()
		template = JINJA_ENVIRONMENT.get_template('index.html')
		if user:	
			#shouldn't put in raw valus, should put them in a template_values dictionary and take from there
			signinstatus = "Log out"
			url = users.create_logout_url('/')
			userinfo = "Logged in as {0}".format(user.email())
			useremail = user.email()
		else:
			signinstatus = "Log in"
			url = users.create_login_url('/')
			userinfo = ''
			useremail = ''
		template_values = {
			'signinstatus': signinstatus,
			'url': url,
			'userinfo': userinfo,
			'useremail': useremail}
		self.response.write(template.render(template_values))
		self.response.write("""<br><br><br><p id="help-text"> Need some help? You can refer to our <a href="help">help page</a></p>""")
		
class Help(webapp2.RequestHandler):
    def get(self):
	# for button that changes depending on whether user is logged in
		user = users.get_current_user()
		template = JINJA_ENVIRONMENT.get_template('help.html')
		if user:	
			#shouldn't put in raw valus, should put them in a template_values dictionary and take from there
			signinstatus = "Log out"
			url = users.create_logout_url('/')
			userinfo = "Logged in as {0}".format(user.email())
			useremail = user.email()
		else:
			signinstatus = "Log in"
			url = users.create_login_url('/')
			userinfo = ''
			useremail = ''
		template_values = {
			'signinstatus': signinstatus,
			'url': url,
			'userinfo': userinfo,
			'useremail': useremail}
		self.response.write(template.render(template_values))
		
class SubmitFront(webapp2.RequestHandler):
    def get(self):						#seems to have an issue with the post instead of get (got 405 method not allowed error)
        # for button that changes depending on whether user is logged in
		user = users.get_current_user()
		#if user is to check if user is already logged in, otherwise user.email will lead to error if user is not logged in 
		if user: 
			#checks if user is logged into account with dhs.sg as the last 6 elements
			if user.email()[-6:] == "dhs.sg":	
				#shouldn't put in raw valus, should put them in a template_values dictionary and take from there
				signinstatus = "Log out"
				url = users.create_logout_url('/submit')
				userinfo = "Logged in as {0}".format(user.email())
				#to change the submit form page depending on whether the user is logged into dhs.sg account
				submitform = """<div id="content-submission">
					<h2> Tell Us Your Story! </h2>  
					<p> Which location would you like to talk about? </p>
					<!-- the form sends the data to the /send page which calls the SubmitBack handler -->
					<form action="/send" method= "post"> 
						<select name="place">
							<option value="ZXY"> Zheng Xin Yuan </option>
							<option value="Hall"> Hall </option>
							<option value="PAC"> Performing Arts Centre (PAC) </option>
							<option value="ISH"> Indoor Sports Hall (ISH) </option>
						</select>
						<p> What would you like to write about the place? </p>
						<textarea id="comment-box" name="comment" placeholder="Enter your comment"></textarea>
						<br>
						<input type="submit" value="Submit Your Story"/>
					</form>
				</div>"""
			else:
				signinstatus = "Log out"
				url = users.create_logout_url('/submit')
				userinfo = "Logged in as {0}".format(user.email())
				submitform = """<p id="response"><br> Please log into your DHS account before writing about your story</p>"""
			
		else:
			signinstatus = "Log in"
			url = users.create_login_url('/submit')
			userinfo = ''
			submitform = """<p id="response"><br> Please log into your DHS account before writing about your story</p>"""
		template_values = {
			'signinstatus': signinstatus,
			'url': url,
			'userinfo': userinfo}
		template = JINJA_ENVIRONMENT.get_template('submit.html')
		self.response.write(template.render(template_values))
		self.response.write(submitform)
		self.response.write("""<br><br><br><p id="help-text"> Need some help? You can refer to our <a href="help">help page</a></p></body></html>""")
#handler to process user input data
class SubmitBack(webapp2.RequestHandler):
	def post(self):
		#gets the data from the previous page, from the different elements in the form with the respective names
		place = self.request.get('place')
		comment = Comment(parent = comment_key(place))
		comment.author = users.get_current_user().email()
		comment.content = self.request.get('comment')
		#I think this puts the data into datastore using the parent datastore key above ^
		comment.put()
		#redirects the user back to the submit page 
		self.redirect('/submit')
		
class Hall(webapp2.RequestHandler):
    def get(self):
        # for button that changes depending on whether user is logged in
		user = users.get_current_user()
		template = JINJA_ENVIRONMENT.get_template('hall.html')
		#queries for the comments from the key and fetches them
		comment_query = Comment.query(ancestor=comment_key("Hall")).order(-Comment.datetime)
		comments = comment_query.fetch(10)
		if user:	
			#shouldn't put in raw valus, should put them in a template_values dictionary and take from there
			signinstatus = "Log out"
			url = users.create_logout_url('/hall')
			userinfo = "Logged in as {0}".format(user.email())
		else:
			signinstatus = "Log in"
			url = users.create_login_url('/hall')
			userinfo = ''
		template_values = {
			'signinstatus': signinstatus,
			'url': url,
			'userinfo': userinfo}
		self.response.write(template.render(template_values))
		self.response.write("""<div id='comment-area'>""")
		#prints the comments below (a div is created for each comment)
		for i in comments:
			if user:
				if user.email() == i.author:
					self.response.out.write("""<div class="comment"><p><strong>%s (You)</strong> wrote:</p>""" % i.author)
				else:
					self.response.out.write("""<div class="comment"><p><strong>%s </strong> wrote:</p>""" % i.author)
			else:
				self.response.out.write("""<div class="comment"><p><strong>%s </strong> wrote:</p>""" % i.author)
			self.response.out.write("""<p>%s</p></div>""" % i.content)
		self.response.out.write("""<br><br><br><p id="help-text"> Need some help? You can refer to our <a href="help">help page</a></p></div></body></html>""")
		
class ZXY(webapp2.RequestHandler):
    def get(self):
        # for button that changes depending on whether user is logged in
		user = users.get_current_user()
		template = JINJA_ENVIRONMENT.get_template('zxy.html')
		#queries for the comments from the key and fetches them
		comment_query = Comment.query(ancestor=comment_key("ZXY")).order(-Comment.datetime)
		comments = comment_query.fetch(10)
		if user:	
			#shouldn't put in raw valus, should put them in a template_values dictionary and take from there
			signinstatus = "Log out"
			url = users.create_logout_url('/zxy')
			userinfo = "Logged in as {0}".format(user.email())
		else:
			signinstatus = "Log in"
			url = users.create_login_url('/zxy')
			userinfo = ''
		template_values = {
			'signinstatus': signinstatus,
			'url': url,
			'userinfo': userinfo}
		self.response.write(template.render(template_values))
		self.response.write("""<div id='comment-area'>""")
		#prints the comments below (a div is created for each comment)
		for i in comments:
			if user:
				if user.email() == i.author:
					self.response.out.write("""<div class="comment"><p><strong>%s (You)</strong> wrote:</p>""" % i.author)
				else:
					self.response.out.write("""<div class="comment"><p><strong>%s </strong> wrote:</p>""" % i.author)
			else:
				self.response.out.write("""<div class="comment"><p><strong>%s </strong> wrote:</p>""" % i.author)
			self.response.out.write("""<p>%s</p></div>""" % i.content)
		self.response.out.write("""<br><br><br><p id="help-text"> Need some help? You can refer to our <a href="help">help page</a></p></div></body></html>""")
		
class PAC(webapp2.RequestHandler):
    def get(self):
        # for button that changes depending on whether user is logged in
		user = users.get_current_user()
		template = JINJA_ENVIRONMENT.get_template('pac.html')
		#queries for the comments from the key and fetches them
		comment_query = Comment.query(ancestor=comment_key("PAC")).order(-Comment.datetime)
		comments = comment_query.fetch(10)
		if user:	
			#shouldn't put in raw valus, should put them in a template_values dictionary and take from there
			signinstatus = "Log out"
			url = users.create_logout_url('/pac')
			userinfo = "Logged in as {0}".format(user.email())
		else:
			signinstatus = "Log in"
			url = users.create_login_url('/pac')
			userinfo = ''
		template_values = {
			'signinstatus': signinstatus,
			'url': url,
			'userinfo': userinfo}
		self.response.write(template.render(template_values))
		self.response.write("""<div id='comment-area'>""")
		#prints the comments below (a div is created for each comment)
		for i in comments:
			if user:
				if user.email() == i.author:
					self.response.out.write("""<div class="comment"><p><strong>%s (You)</strong> wrote:</p>""" % i.author)
				else:
					self.response.out.write("""<div class="comment"><p><strong>%s </strong> wrote:</p>""" % i.author)
			else:
				self.response.out.write("""<div class="comment"><p><strong>%s </strong> wrote:</p>""" % i.author)
			self.response.out.write("""<p>%s</p></div>""" % i.content)
		self.response.out.write("""<br><br><br><p id="help-text"> Need some help? You can refer to our <a href="help">help page</a></p></div></body></html>""")

class ISH(webapp2.RequestHandler):
    def get(self):
        # for button that changes depending on whether user is logged in
		user = users.get_current_user()
		template = JINJA_ENVIRONMENT.get_template('ish.html')
		#queries for the comments from the key and fetches them
		comment_query = Comment.query(ancestor=comment_key("ISH")).order(-Comment.datetime)
		comments = comment_query.fetch(10)
		if user:	
			#shouldn't put in raw valus, should put them in a template_values dictionary and take from there
			signinstatus = "Log out"
			url = users.create_logout_url('/ish')
			userinfo = "Logged in as {0}".format(user.email())
		else:
			signinstatus = "Log in"
			url = users.create_login_url('/ish')
			userinfo = ''
		template_values = {
			'signinstatus': signinstatus,
			'url': url,
			'userinfo': userinfo}
		self.response.write(template.render(template_values))
		self.response.write("""<div id='comment-area'>""")
		#prints the comments below (a div is created for each comment)
		for i in comments:
			if user:
				if user.email() == i.author:
					self.response.out.write("""<div class="comment"><p><strong>%s (You)</strong> wrote:</p>""" % i.author)
				else:
					self.response.out.write("""<div class="comment"><p><strong>%s </strong> wrote:</p>""" % i.author)
			else:
				self.response.out.write("""<div class="comment"><p><strong>%s </strong> wrote:</p>""" % i.author)
			self.response.out.write("""<p>%s</p></div>""" % i.content)
		self.response.out.write("""<br><br><br><p id="help-text"> Need some help? You can refer to our <a href="help">help page</a></p></div></body></html>""")
		
app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/submit', SubmitFront),
	('/send', SubmitBack),
	('/hall', Hall),
	('/pac', PAC),
	('/zxy', ZXY),
	('/ish', ISH),
	('/help', Help)
], debug=True)
