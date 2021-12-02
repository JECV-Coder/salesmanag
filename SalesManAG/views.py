from django.http import HttpResponse
import random
import operator
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.template import loader

class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self, city):
        xDis = abs(self.x - city.x)
        yDis = abs(self.y - city.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance
    
    def __repr__(self):
        return "" + str(self.x) + "," + str(self.y) + ""

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness= 0.0
        
    def routeDistance(self):
        if self.distance ==0:
            pathDistance = 0
            for i in range(0, len(self.route)):
                fromCity = self.route[i]
                toCity = None
                if i + 1 < len(self.route):
                    toCity = self.route[i + 1]
                else:
                    toCity = self.route[0]
                pathDistance += fromCity.distance(toCity)
            self.distance = pathDistance
        return self.distance

    def routeFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.routeDistance())
        return self.fitness
    
    
def createRoute(cityList):
    route = random.sample(cityList, len(cityList))
    return route

def initialPopulation(popSize, cityList):
    population = []

    for i in range(0, popSize):
        population.append(createRoute(cityList))
    return population
    
def rankRoutes(population):
    fitnessResults = {}
    for i in range(0,len(population)):
        fitnessResults[i] = Fitness(population[i]).routeFitness()
    return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)

def selection(popRanked, eliteSize):
    selectionResults = []
    df = pd.DataFrame(np.array(popRanked), columns=["Index","Fitness"])
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
    
    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100*random.random()
        for i in range(0, len(popRanked)):
            if pick <= df.iat[i,3]:
                selectionResults.append(popRanked[i][0])
                break
    return selectionResults

def matingPool(population, selectionResults):
    matingpool = []
    for i in range(0, len(selectionResults)):
        index = selectionResults[i]
        matingpool.append(population[index])
    return matingpool

def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []
    
    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))
    
    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        childP1.append(parent1[i])
        
    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    return child

def breedPopulation(matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(0,eliteSize):
        children.append(matingpool[i])
    
    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool)-i-1])
        children.append(child)
    return children

def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(individual))
            
            city1 = individual[swapped]
            city2 = individual[swapWith]
            
            individual[swapped] = city2
            individual[swapWith] = city1
    return individual

def nextGeneration(currentGen, eliteSize, mutationRate):
    popRanked = rankRoutes(currentGen)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(matingpool, eliteSize)
    nextGeneration = mutate(children, mutationRate)
    return nextGeneration

def geneticAlgorithmPlot(population, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(popSize, population)
    #print("Initial distance: " + str(1 / rankRoutes(pop)[0][1]))
    progress = []
    progressMax = []
    progress.append(1 / rankRoutes(pop)[0][1])
    progressMax.append(1 / rankRoutes(pop)[popSize-1][1])

    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)
        aux = rankRoutes(pop)[0][1]
        progress.append(1 / aux)
        progressMax.append(1 / rankRoutes(pop)[popSize-1][1])
        print("Generacion "+str(i)+" distancia "+str(1 / aux))
    #print("Final distance: " + str(1 / rankRoutes(pop)[0][1]))
    plt.plot(progress,label="Min")
    plt.plot(progressMax,label="Max")
    plt.ylabel('Distance')
    plt.xlabel('Generation')
    plt.legend(loc='best')
    plt.show()
    
    bestRouteIndex = rankRoutes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]
    return bestRoute

def maps(request):
    cityList = []

    
    
    getPopSize = request.GET["poblacion"]
    getEliteSize = request.GET["elite"]
    getMutationRate = request.GET["mutacion"]
    getGenerations = request.GET["generaciones"]
    getPopulation = request.GET["coordenadas"]
    if getPopulation == "":
        for i in range(0,25):
            cityList.append(City(x=int(random.random() * 20), y=int(random.random() * 20)))
    else:
        values = getPopulation.split()
        for i in values:
            point = i.split(sep=',')
            print(point[0],point[1])
            cityList.append(City(x=float(point[0]),y=float(point[1])))
            cityList.append(City(x=float(point[0]),y=float(point[1])))
    routeContext = geneticAlgorithmPlot(population=cityList, popSize=int(getPopSize), eliteSize=int(getEliteSize), mutationRate=float(getMutationRate), generations=int(getGenerations))
    primerValor = []
    primerValor.append(routeContext[0])
    datos=""
    contador = 0
    while contador<len(routeContext):
        datos = datos+"["+str(routeContext.pop(contador))+"],"
        contador = contador + 1
    datos=datos+"["+str(primerValor[0])+"]"
    primerDato = str(primerValor.pop(0))
    print(datos)
    doc = """
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <title>Document</title>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no" />
                <script src='https://api.mapbox.com/mapbox-gl-js/v2.1.1/mapbox-gl.js'></script>
                <link href='https://api.mapbox.com/mapbox-gl-js/v2.1.1/mapbox-gl.css' rel='stylesheet' />
                <style>
                    body { margin: 0; padding: 0; }
                    #map { position: absolute; top: 0; bottom: 0; width: 100%; }
                </style>
            </head>
            <body>
                <div id='map'></div>
                <script>
                    mapboxgl.accessToken = 'pk.eyJ1IjoiZGFlZHJpYzY5IiwiYSI6ImNrbDhoMDgwYjF3Ym4zMm5yZWRwdWZqOGIifQ.vW0jdaQ8PJHPg6kLGyVWiA';
                    var map = new mapboxgl.Map({
                        container: 'map',
                        style: 'mapbox://styles/mapbox/streets-v11',
                        center: ["""+str(primerDato)+"""],
                        zoom: 15
                    });
                    map.on('load', function () {
                    map.addSource('route', {
                        'type': 'geojson',
                        'data': {
                            'type': 'Feature',
                            'properties': {},
                            'geometry': {
                                'type': 'LineString',
                                'coordinates': ["""+str(datos)+"""]
                            }
                        }
                    }
                    
                    );
                    map.addLayer({
                        'id': 'route',
                        'type': 'line',
                        'source': 'route',
                        'layout': {
                            'line-join': 'round',
                            'line-cap': 'round'
                        },
                        'paint': {
                            'line-color': '#FF0059',
                            'line-width': 8
                        }
                    });
                    });
                </script>
            </body>
            </html>
    """
    return HttpResponse(doc)

def valores(request):
    return render(request,"parametros.html")