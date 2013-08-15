import requests
import argparse
from xml.dom.minidom import parseString

debug = False

def getAgencyList():
	c = do_request({'command': 'agencyList'})
	xmlDom = parseString(c)
	agencies = xmlDom.getElementsByTagName('agency')
	for agency in agencies:
		print ("tag: %s \t title: %s \t regionTitle: %s" % 
			(agency.attributes['tag'].value, agency.attributes['title'].value, 
			agency.attributes['regionTitle'].value))
	return agencies

def getRouteList(agency):
	c = do_command(agency, 'routeList')
	xmlDom = parseString(c)
	routes = xmlDom.getElementsByTagName('route')
	for route in routes:
		print ("tag: %s\t title: %s" % (route.attributes['tag'].value, 
			route.attributes['title'].value))
	return routes

def getRouteStops(agency, route):
	c = do_command(agency, 'routeConfig', {'r': route})
	xmlDom = parseString(c)
	stops = [e for e in xmlDom.getElementsByTagName('route')[0].childNodes
				if e.nodeType == e.ELEMENT_NODE and e.tagName == "stop"]
	for stop in stops:
		print ("stopId: %s\t tag: %s\t title: %s\t" % (
			stop.attributes['stopId'].value,
			stop.attributes['tag'].value,
			stop.attributes['title'].value))
	return stops

def getRouteDirections(agency, route):
	c = do_command(agency, 'routeConfig', {'r': route})
	xmlDom = parseString(c)
	directions = [e for e in xmlDom.getElementsByTagName('direction')
				if e.nodeType == e.ELEMENT_NODE]
	for direction in directions:
		print ("tag: %s\t name: %s\t title: %s\t" % (
			direction.attributes['tag'].value,
			direction.attributes['name'].value,
			direction.attributes['title'].value))
	return directions

def getPrediction(agency, route, stop):
	c = do_command(agency, 'predictions', {'r': route, 's': stop})
	xmlDom = parseString(c)
	predictions = xmlDom.getElementsByTagName('predictions')[0]
	print ("== %s at %s ==" % (predictions.attributes['routeTitle'].value, 
		predictions.attributes['stopTitle'].value))
	directions = [e for e in xmlDom.getElementsByTagName('direction')
				if e.nodeType == e.ELEMENT_NODE]
	for direction in directions:
		predictions = [e for e in direction.childNodes 
						if e.nodeType == e.ELEMENT_NODE 
							and e.tagName == "prediction"]
		for prediction in predictions:
			print ("dir_tag: %s\t direction: %s\t block: %s\t"
				" min: %s\t sec: %s\t" % (
					prediction.attributes['dirTag'].value,
					direction.attributes['title'].value,
					prediction.attributes['block'].value,
					prediction.attributes['minutes'].value,
					prediction.attributes['seconds'].value
					))
	return directions	

def do_command(agency, command, rargs={}):
	params = {'command': command, 'a': agency};
	params.update(rargs);
	return do_request(params)

def do_request(rargs={}):
	r = requests.get('http://webservices.nextbus.com/'
			'service/publicXMLFeed', params=rargs)
	if debug:
		print "Debug URL: %s" % r.url
	return r.text

def main():
	parser = argparse.ArgumentParser(description='SF-Muni command line tool')
	
	# actions list
	parser.add_argument('--agencyList', action='store_true',
		help='List all agencys in NextBus')
	parser.add_argument('--routeList', action='store_true',
		help='List all routes in an --agency')
	parser.add_argument('--routeStops', action='store_true',
		help='List all stops in a --route for and --agency')
	parser.add_argument('--routeDirections', action='store_true',
		help='List all directions for a --route for and --agency')
	parser.add_argument('--stopPredictions', action='store_true',
		help='List all directions for a --route, --agency and --stop')

	# params
	parser.add_argument('--agency', help='nextbus agency')
	parser.add_argument('--route', help='route')
	parser.add_argument('--stop', help='stop')
	
	# options
	parser.add_argument('--verbose', action='store_true',
		help='outputs more information on every request')

	args = parser.parse_args()

	global debug
	debug = args.verbose

	if args.agencyList:
		getAgencyList()
	elif args.routeList and args.agency:
		getRouteList(args.agency)
	elif args.routeStops and args.agency and args.route:
		getRouteStops(args.agency, args.route)
	elif args.routeDirections and args.agency and args.route:
		getRouteDirections(args.agency, args.route)
	elif args.stopPredictions and args.agency and args.route and args.stop:
		getPrediction(args.agency, args.route, args.stop)

if __name__ == "__main__":
	main()