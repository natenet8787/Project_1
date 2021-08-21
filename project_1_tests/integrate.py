#Packages needed for triangle arb 
#The bellman ford algo is in the math package
import json, urllib.request, sys, math, re
import numpy as np

#Packages needed for twilio notification
import os
from twilio.rest import Client
from dotenv import load_dotenv

#Packages needed for integration between packages
from plyer import notification


#empty list and dic needed to properly graph endpoints
graph = {}
paths = []



#Main function below that runs finds the shortest path rate, and hence the arb opportunity
def main():
    forex_rates = get_rates()
    print("Current Forex Rates:")
    print(forex_rates)
    print("\n")
    gr = get_graph(forex_rates) #gets the current forex rates
    
    for key in graph: 
        path = bellman_ford(graph, key)
        if path not in paths and not None:
            paths.append(path)

    for path in paths:
        if path == None:
            print("No Arbitrage opportunity detected in current rates :(")
        else:
            money = 100 #base amount of currency we are starting with
            
            notification.notify(title= "<---Arbitrage cycle detected--->",
                    message= "Starting with %(money)i in %(currency)s" % {"money":money,"currency":path[0]},
                    app_icon = None,
                    timeout= 30,
                    toast=False)

            load_dotenv() 

            #account notification for twilio texting       
            #account_sid = 'ACcd99d0ef7c6e5a8788f01331229a6bae'
            #auth_token = '7b43a079792a7fae40b49120c09cdf97'
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            print(account_sid, auth_token)
            client = Client(account_sid, auth_token)

            #This tells the user if there is any arb opportunites available
            print("<---Arbitrage cycle detected--->")
            print("Starting with %(money)i in %(currency)s" % {"money":money,"currency":path[0]})

            #Displays the paths available and prints out the oppositite path as well
            for i,value in enumerate(path):
                if i+1 < len(path):
                    start = path[i]
                    end = path[i+1]
                    rate = math.exp(-graph[start][end])
                    money *= rate
                    print("%(start)s to %(end)s at a rate of %(rate)f = %(money)f" % {"start":start,"end":end,"rate":rate,"money":money})

            #Message to be send via text
            message = client.messages \
                    .create(
                    body="%(start)s to %(end)s at a rate of %(rate)f = %(money)f" % {"start":start,"end":end,"rate":rate,"money":money},
                    from_='+19416134207',
                    to='+15165547061'
                       )    
        print("\n")


#This function gets the current rate via this base API 
def get_rates():
    try:
        forex_url = urllib.request.urlopen("http://fx.priceonomics.com/v1/rates/")
        forex_r = forex_url.read()
        rates = json.loads(forex_r)
    except Exception as e:
        print >>sys.stderr, "Error getting rates:", e
        sys.exit(1)
    
    return rates


#Graph function that takes the rates from the API and sends it to the graph prior to running bellman ford
def get_graph(forex_rates):
    pattern = re.compile("([A-Z]{3})_([A-Z]{3})")
    for key in forex_rates:
        matches = pattern.match(key)
        conversion_rate = -math.log(float(forex_rates[key]))
        from_rate = matches.group(1)
        to_rate = matches.group(2)
        if from_rate != to_rate:
            if from_rate not in graph:
                graph[from_rate] = {}
            graph[from_rate][to_rate] = float(conversion_rate)
    return graph

#Uses the graphs we created to start finding the distances from each other
def initialize(graph, source):
    d = {} # Stands for destination
    p = {} # Stands for predecessor
    for node in graph:
        d[node] = float('Inf') # We start admiting that the rest of nodes are very very far
        p[node] = None
    d[source] = 0 # For the source we know how to reach
    return d, p    

#bellford #1
def relax(node, neighbor, graph, d, p):
    # If the distance between the node and the neighbor is lower than the one I have now
    if d[neighbor] > d[node] + graph[node][neighbor]:
        # Record this lower distance
        d[neighbor]  = d[node] + graph[node][neighbor]
        p[neighbor] = node    


#retrace function
def retrace_negative_loop(p, start):
    arbitrageLoop = [start]
    next_node = start
    while True:
        next_node = p[next_node]
        if next_node not in arbitrageLoop:
            arbitrageLoop.append(next_node)
        else:
            arbitrageLoop.append(next_node)
            arbitrageLoop = arbitrageLoop[arbitrageLoop.index(next_node):]
            return arbitrageLoop


#Final step of bellman_ford algo which finds the convergance
def bellman_ford(graph, source):
    d, p = initialize(graph, source)
    for i in range(len(graph)-1): #Run this until is converges
        for u in graph:
            for v in graph[u]: #For each neighbor of u
                relax(u, v, graph, d, p) #Lets relax it


    # Step 3: check for negative-weight cycles
    for u in graph:
        for v in graph[u]:
            if d[v] < d[u] + graph[u][v]:
                return(retrace_negative_loop(p, source))
    return None



#main function 
if __name__ == '__main__':
    main()    