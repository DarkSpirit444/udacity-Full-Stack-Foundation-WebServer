from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

import sys
sys.path.insert(0, '/vagrant/fullstack')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

class webserverHandler(BaseHTTPRequestHandler):
	engine = create_engine('sqlite:////vagrant/fullstack/restaurantmenu.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind = engine)
	session = DBSession()

	def do_GET(self):
		try:
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = "<html><body>"
				output += "Hello!"				
				output += "<form method='POST' enctype='multipart/form-data' action='hello'>\
							<h2>What would you like me to say?</h2><input name='message' type='text'>\
							<input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = "<html><body>"
				output += "&#161Hola <a href = '/hello'>Back to Hello</a>"
				output += "<form method='POST' enctype='multipart/form-data' action='hello'>\
							<h2>What would you like me to say?</h2><input name='message' type='text'>\
							<input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = "<html><body><ul id=\"navcontainer\" style=\"list-style-type:none;margin:0;padding:0;\">"
				self.session.query(Restaurant).all()
				restaurants = self.session.query(Restaurant)
				for restaurant in restaurants:
					output += "<li><ul style=\"list-style-type:none;margin:0;padding:0;\"><li>%s</li><li><a href=\"/restaurants/%s/edit\">Edit</a></li><li><a href=\"/restaurants/%s/delete\">Delete</a></li></ul><br/></li>" % (restaurant.name, restaurant.id, restaurant.id)
				output += "</ul><br/><a href=\"/restaurants/new\">Make a New Restaurant Here</a></body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = "<html><body>"
				output += "<h1>Make a New Restaurant</h1>"		
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>\
							<input name='new_restaurant' type='text'>\
							<input type='submit' value='Create'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/edit"):
				restaurant_id = self.path.split("/")[2]
				restaurant = self.session.query(Restaurant).filter_by(id = restaurant_id).one()
				if restaurant != [] :
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()

					output = "<html><body>"
					output += "<h1>%s</h1>" % restaurant.name	
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>\
								<input name='restaurant_new_name' type='text' placeholder =\"%s\">\
								<input type='submit' value='Rename'></form>" % (restaurant.id, restaurant.name)
					output += "</body></html>"
					self.wfile.write(output)
					print output
				return

			if self.path.endswith("/delete"):
				restaurant_id = self.path.split("/")[2]
				restaurant = self.session.query(Restaurant).filter_by(id = restaurant_id).one()
				if restaurant != [] :
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()

					output = "<html><body>"
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/delete'>\
								<h1>Are you sure you want to delete %s?</h1>\
								<input type='submit' value='Delete'></form>" % (restaurant.id, restaurant.name)
					output += "</body></html>"
					self.wfile.write(output)
					print output
				return

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)

			if self.path.endswith("hello"):
				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				messagecontent = fields.get('message')

				output = ""
				output += "<html><body>"
				output += " <h2> Okay, how about this: </h2>"
				output += "<h1> %s </h1>" % messagecontent[0]

				output += "<form method='POST' enctype='multipart/form-data' action='hello'>\
							<h2>What would you like me to say?</h2><input name='message' type='text'>\
							<input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				self.end_headers()

			elif self.path.endswith("/restaurants/new"):
				new_restaurant = fields.get('new_restaurant')

				restaurant1 = Restaurant(name=new_restaurant[0])
				self.session.add(restaurant1)
				self.session.commit()
				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()

			elif self.path.endswith("/edit"):
				restaurant_new_name = fields.get('restaurant_new_name')
				restaurant_id = self.path.split("/")[2]

				restaurant1 = self.session.query(Restaurant).filter_by(id = restaurant_id).one()
				if restaurant1 != [] :
					restaurant1.name = restaurant_new_name[0]
					self.session.add(restaurant1)
					self.session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

			elif self.path.endswith("/delete"):
				restaurant_id = self.path.split("/")[2]

				restaurant1 = self.session.query(Restaurant).filter_by(id = restaurant_id).one()
				if restaurant1 != [] :
					self.session.delete(restaurant1)
					self.session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')	
					self.end_headers()			
		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

if __name__ == '__main__':
	main()