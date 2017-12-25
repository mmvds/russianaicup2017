from model.ActionType import ActionType
from model.VehicleType import VehicleType
from model.FacilityType import FacilityType
from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.World import World
import numpy as np
from scipy.cluster.vq import vq, kmeans, whiten
myVehicleIds = []
myVehicleIdsByType = [[],[],[],[],[]]
clustersX = [[],[],[],[],[]]
clustersY = [[],[],[],[],[]]
enemyVehicleIds = []
enemyVehicleIdsByType = [[],[],[],[],[]]
vehicleById = {}
facilityById = {}
updateTickByVehicleId = {}
mu = [] 
muNuke = [] 
K = 5
KK = 20
I = 10
bestdist = []
minDist = {}
minDist[VehicleType.ARRV] = 18 + 0.9 * 31 - 0.4 * 30 * 0.6
minDist[VehicleType.IFV] = 18 + 0.9 * 31 - 0.4 * 30 * 0.6
minDist[VehicleType.TANK] = 18 + 0.9 * 31 - 0.3 * 30 * 0.6
minDist[VehicleType.FIGHTER] = 20 + 1.2 * 31 - 1.2 * 30 * 0.6
minDist[VehicleType.HELICOPTER] = 20 + 1.2 * 31 - 0.9 * 30 * 0.6
maxDist = {}
maxDist[VehicleType.ARRV] = 60 * 0.8 - 0.4 * 0.6
maxDist[VehicleType.IFV] = 80 * 0.8 - 0.4 * 0.6
maxDist[VehicleType.TANK] = 80 * 0.8 - 0.3 * 0.6
maxDist[VehicleType.FIGHTER] = 120 * 0.6 - 1.2 * 0.6
maxDist[VehicleType.HELICOPTER] = 100 * 0.6 - 0.9 * 0.6
attacks = [{},{},{},{},{}]
attacks[VehicleType.TANK] = dict([(VehicleType.TANK, 20), (VehicleType.IFV, 40), (VehicleType.HELICOPTER, 20), (VehicleType.FIGHTER, 0), (VehicleType.ARRV, 50)])
attacks[VehicleType.IFV] = dict([(VehicleType.TANK, 10), (VehicleType.IFV, 30), (VehicleType.HELICOPTER, 40), (VehicleType.FIGHTER, 10), (VehicleType.ARRV, 40)])
attacks[VehicleType.HELICOPTER] = dict([(VehicleType.TANK, 40), (VehicleType.IFV, 20), (VehicleType.HELICOPTER, 40), (VehicleType.FIGHTER, 10), (VehicleType.ARRV, 80)])
attacks[VehicleType.FIGHTER] = dict([(VehicleType.TANK, 0), (VehicleType.IFV, 0), (VehicleType.HELICOPTER, 60), (VehicleType.FIGHTER, 30), (VehicleType.ARRV, 0)])
attacks[VehicleType.ARRV] = dict([(VehicleType.TANK, 0), (VehicleType.IFV, 0), (VehicleType.HELICOPTER, 0), (VehicleType.FIGHTER, 0), (VehicleType.ARRV, 0)])
myV = -1
enV = -1
lastNukaTick = 0
frame = 40
movements = []
round2 = False
minefield = False
fieldChecker = [[],[],[],[],[]]
scaleFactor = 1.5
maxGroup = 0
centerGroups = {}
deadGroups = []
muNA = []

def getCoords(points):
    x=[]
    y=[]
    for p in points:
        x.append(p.x)
        y.append(p.y)
    return min(x) - 2, max(x) + 2 , min(y) - 2 , max(y) + 2

class MyStrategy:
    def move(self, me: Player, world: World, game: Game, move: Move):
        global vtDict, vehicleById, updateTickByVehicleId, facilityById
        global myVehicleIds, myVehicleIdsByType, enemyVehicleIds, enemyVehicleIdsByType
        global mu, muNuke, K, KK, lastNukaTick
        global minDist, maxDist, bestdist
        global myV, enV
        global clustersX, clustersY, frame
        global movements
        global round2, minefield, fieldChecker
        global scaleFactor, maxGroup, centerGroups, deadGroups
        global attacks, muNA
        myId=world.get_my_player().id
        enemy=world.get_opponent_player()
        enemyId=enemy.id
        wti=world.tick_index
        nsr=game.tactical_nuclear_strike_radius
        nsd=game.tactical_nuclear_strike_delay
        for v in world.new_vehicles:
            vehicleById[v.id] = v
            updateTickByVehicleId[v.id] = wti
            if v.player_id == myId:
                myVehicleIds.append(v.id)
                myVehicleIdsByType[v.type].append(v.id)
            else:
                enemyVehicleIds.append(v.id)
                enemyVehicleIdsByType[v.type].append(v.id)

        for v in world.vehicle_updates:
            if v.durability == 0:
                if v.id in myVehicleIds:
                    myVehicleIds.pop(myVehicleIds.index(v.id))
                    myVehicleIdsByType[vehicleById[v.id].type].pop(myVehicleIdsByType[vehicleById[v.id].type].index(v.id))
                else:
                    enemyVehicleIds.pop(enemyVehicleIds.index(v.id))
                    enemyVehicleIdsByType[vehicleById[v.id].type].pop(enemyVehicleIdsByType[vehicleById[v.id].type].index(v.id))
                vehicleById.pop(v.id)
                updateTickByVehicleId.pop(v.id)
            else:
                vehicleById[v.id].update(v)
                updateTickByVehicleId[v.id] = wti
        for f in world.facilities:
                facilityById[f.id] = f

        if wti == 0:
            if world.facilities:
                round2 = True
            if round2 == False:
                for i in range (0,5):
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.vehicle_type = '+str(i)+'; move.right = world.width; move.bottom = world.height',0,'building'])
                    arr = []
                    for v in vehicleById.values():
                        if v.type == i:
                            arr.append(v)
                    movements.append(['move.action = ActionType.SCALE; move.x, move.y = ' + str(min([v.x for v in arr]) - 10) + ', ' + str(min([v.y for v in arr]) - 10) +'; move.factor = 10.0',1,'building'])
            else:
                for i in [VehicleType.FIGHTER, VehicleType.HELICOPTER]:
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.vehicle_type = '+str(i)+'; move.right = world.width; move.bottom = world.height',0,'building'])
                    arr = []
                    for v in vehicleById.values():
                        if (v.type == i) &(v.player_id == me.id):
                            arr.append(v)
                    movements.append(['move.action = ActionType.SCALE; move.x, move.y = ' + str(min([v.x for v in arr]) - 10) + ', ' + str(min([v.y for v in arr]) - 10) +'; move.factor = 10.0',1,'building'])
                muNA = []
                notAerial = []
                for i in [VehicleType.ARRV, VehicleType.IFV, VehicleType.TANK]:
                    arr = []
                    for v in vehicleById.values():
                        if (v.type == i) &(v.player_id == me.id):
                            arr.append(v)
                            notAerial.append(v)
                    w = max([v.x for v in arr])- min([v.x for v in arr])
                    h = max([v.y for v in arr])- min([v.y for v in arr])
                    
                    if len(facilityById) > 2:
                        muNA.append([min([v.x for v in arr])+w/4, min([v.y for v in arr])+h/4])
                        muNA.append([min([v.x for v in arr])+3*w/4, min([v.y for v in arr])+h/4])
                        muNA.append([min([v.x for v in arr])+w/4, min([v.y for v in arr])+3*h/4])
                        muNA.append([min([v.x for v in arr])+3*w/4, min([v.y for v in arr])+3*h/4])
                    
                sortedMu = []
                sortedFacilities = []
                ZeroPoint = [np.mean([ v.x for v in notAerial]), np.mean([ v.y for v in notAerial])]
                distFromZero = []
                for i in range(1,len(world.facilities)+1):
                    f = facilityById[i]
                    distFromZero.append((f.left + 32 - ZeroPoint[0])**2 + (f.top + 32 - ZeroPoint[1])**2)

                while sum(distFromZero) != 0:
                    ind = distFromZero.index(max(distFromZero))
                    sortedFacilities.append(ind+1)
                    distFromZero[ind] = 0

                if len(sortedFacilities) > len(muNA):
                    sortedFacilities = sortedFacilities[len(sortedFacilities) - len(muNA):]
                
                for i in range(0,len(sortedFacilities)):
                    f=facilityById[sortedFacilities[i]]
                    minDistToFacilities = 10000000
                    for j in range(0,len(muNA)):
                        dst = (muNA[j][0] - f.left - 32)**2 + (muNA[j][1] - f.top - 32)**2
                        if dst < minDistToFacilities:
                            minDistToFacilities = dst
                            nearest = j
                    sortedMu.append(muNA.pop(nearest))
                while muNA:
                    minDistToZero = 10000000
                    for i in range(0,len(muNA)):
                        c=muNA[i]
                        dst = c[0]**2 + c[1]**2
                        if dst < minDistToZero:
                            minDistToZero = dst
                            ind = i
                    sortedMu.append(muNA.pop(ind))

                clustersNotAerial = []
                for i in range(0,len(sortedMu)):
                    clustersNotAerial.append([])
                for i in range(0, len(notAerial)):
                    distFromCenters = []
                    for center in sortedMu:
                        distFromCenters.append((notAerial[i].x - center[0])**2 + (notAerial[i].y - center[1])**2)
                    ind = distFromCenters.index(min(distFromCenters))
                    clustersNotAerial[ind].append(notAerial[i])

                last = 0
                for i in range(0,len(sortedMu)):
                    counts = np.bincount([v.type for v in clustersNotAerial[i]])
                    t = np.argmax(counts)
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = ' +str(getCoords(clustersNotAerial[i])) + '; move.type = ' + str(t) ,0,'start'])
                    movements.append(['move.action = ActionType.SCALE; move.factor = 0.1; move.x, move.y = '+ str(sortedMu[i][0]) + ', ' + str(sortedMu[i][1]), 2, 'start']) 
                    maxGroup += 1
                    movements.append(['move.action = ActionType.ASSIGN; move.group = ' + str(maxGroup),1,'start'])
                    
                    if (last < len(sortedFacilities)) & (i in [2,6,10]):
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.group = ' + str(1+last), 0, 'start'])
                        movements.append(['move.action = ActionType.MOVE; move.x, move.y = '+ str(facilityById[sortedFacilities[last]].left + 32 - sortedMu[last][0]) + ', ' + str(facilityById[sortedFacilities[last]].top + 32 - sortedMu[last][1]), 1, 'start']) 
                        last +=1
                while last<len(sortedFacilities):
                        movements.append(['pause',0,'start',58])
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.group = ' + str(1+last), 0, 'start'])
                        movements.append(['move.action = ActionType.MOVE; move.x, move.y = '+ str(facilityById[sortedFacilities[last]].left + 32 - sortedMu[last][0]) + ', ' + str(facilityById[sortedFacilities[last]].top + 32 - sortedMu[last][1]), 1, 'start']) 
                        last +=1
                        
        if enemyVehicleIds:
            if round2 == False:
                if (wti % 100 == 1) & (wti < 302):
                    for i in range(0,5):
                        fieldChecker[i].append(min([vehicleById[j].get_distance_to(1023,1023) for j in enemyVehicleIdsByType[i]]))
                if wti==302:
                    minefield = True
                    for i in range(0,5):
                        if fieldChecker[i] != sorted(fieldChecker[i]):
                            minefield = False
                    if (abs(fieldChecker[VehicleType.FIGHTER][3] - fieldChecker[VehicleType.FIGHTER][2])>3) | (abs(fieldChecker[VehicleType.HELICOPTER][3] - fieldChecker[VehicleType.HELICOPTER][2])>3):
                        minefield = False
                    if minefield:
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height', 0, 'antifield'])
                        movements.append(['move.action = ActionType.MOVE; move.x, move.y = -500, 0', 1, 'antifield']) 
        
        #Если враг - ковер, делаем сосиску и сидим в углу
        if minefield:
            i = 0
            if movements:
                i = movements[0][1]

            if wti==800:
                movements.insert(i, ['move.action = ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height', 0, 'antifield'])
                movements.insert(i+1, ['move.action = ActionType.MOVE; move.x, move.y = -300, -300', 1, 'antifield']) 
            elif wti==1000:
                movements.insert(i, ['move.action = ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height; move.vehicle_type = VehicleType.FIGHTER', 0, 'antifield'])
                movements.insert(i+1, ['move.action = ActionType.MOVE; move.x, move.y = 0, -200', 1, 'antifield'])
                movements.insert(i+2, ['move.action = ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height; move.vehicle_type = VehicleType.HELICOPTER', 0, 'antifield'])
                movements.insert(i+3, ['move.action = ActionType.MOVE; move.x, move.y = 0, -200', 1, 'antifield'])
            elif (wti < 19000)&(wti > 1000)&(wti % 1500==0):
                movements.insert(i, ['move.action = ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height', 0, 'antifield'])
                movements.insert(i+1, ['move.action = ActionType.MOVE; move.x, move.y = 500, 100', 1, 'antifield'])
            elif (wti < 19000)&(wti > 3999)&(wti > 3999)&(wti % 1500==500):
                movements.insert(i, ['move.action = ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height', 0, 'antifield'])
                movements.insert(i+1, ['move.action = ActionType.MOVE; move.x, move.y = -500, -100', 1, 'antifield'])
            elif wti==19000:
                movements.insert(i, ['move.action = ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height; move.vehicle_type = VehicleType.HELICOPTER', 0, 'antifield'])
                movements.insert(i+1, ['move.action = ActionType.MOVE; move.x, move.y = 700, 700; move.max_speed = 0.6', 1, 'antifield'])
                movements.insert(i+2, ['move.action = ActionType.CLEAR_AND_SELECT; move.right = world.width; move.bottom = world.height; move.vehicle_type = VehicleType.FIGHTER', 0, 'antifield'])
                movements.insert(i+3, ['move.action = ActionType.MOVE; move.x, move.y = 700, 700; move.max_speed = 0.6', 1, 'antifield'])

        #Если на нас сбросили
        if (enemy.next_nuclear_strike_tick_index - wti == nsd - 1) & ((minefield==False) | (minefield & (wti < 19000))):
            i = 0
            if movements:
                i = movements[0][1]
            movements.insert(i, ['move.action = ActionType.CLEAR_AND_SELECT; move.left = ' + str(enemy.next_nuclear_strike_x - nsr) + '; move.right = ' + str(enemy.next_nuclear_strike_x + nsr) + '; move.top = ' + str(enemy.next_nuclear_strike_y - nsr) + '; move.bottom = ' + str(enemy.next_nuclear_strike_y + nsr),0,'escape'])
            movements.insert(i+1, ['move.action = ActionType.SCALE; move.x, move.y = ' + str(enemy.next_nuclear_strike_x) + ', ' + str(enemy.next_nuclear_strike_y) + '; move.factor = 2.0',1,'escape'])

        #Если можно сбросить
        if (me.remaining_nuclear_strike_cooldown_ticks == 0) & (wti % 30 == 0): 
            xNuke = [[vehicleById[i].x, vehicleById[i].y] for i in enemyVehicleIds]
            muNuke = []
            kNuke = KK
            if len(xNuke) < kNuke:
                kNuke = len(xNuke)
            if kNuke != 0:
                muNuke = kmeans(xNuke, kNuke)[0]
                distances = []
                for c in range(0,len(muNuke)):
                    maxD = 0
                    maxDI = -1
                    for i in myVehicleIds:
                        v = vehicleById[i]
                        vDist = v.get_distance_to(muNuke[c][0],muNuke[c][1])
                        if (vDist > minDist[v.type])&(vDist < maxDist[v.type])&(vDist > maxD):
                            maxD = vDist
                            maxDI = i
                    distances.append([muNuke[c][0], muNuke[c][1], maxD, maxDI])
                maxDamage = 0
                for d in distances:
                    if d[3] != -1:
                        damage = 0
                        for i in enemyVehicleIds:
                            v = vehicleById[i]
                            disNuc = v.get_distance_to(d[0],d[1])
                            if disNuc < 50.0:
                                damageForUnit = 100 - (disNuc + 0.5) * 2 
                                if (v.durability - damageForUnit) <= 0:
                                    damage += 1
                                else:
                                    damage += (100 - (disNuc * 2 + 1)) / 100.0
                                    if v.type == VehicleType.ARRV:
                                        damage -= 1.23 #1230 * 0.1 / 100 old formula: damage -= (100 - (disNuc * 2 + 1)) / 1000.0
                        if damage > maxDamage:
                            maxDamage = damage
                            bestdist = d
                if maxDamage > 0.5: #maxDamage > len(enemyVehicleIds) / (kNuke * 15)
                    i = 0
                    if movements:
                        i = movements[0][1]
                    lastNukaTick = wti
                    movements.insert(i, ['move.action = ActionType.TACTICAL_NUCLEAR_STRIKE; move.x = ' + str(bestdist[0]) + '; move.y = ' + str(bestdist[1]) + '; move.vehicle_id = ' + str(bestdist[3]), 0, 'nuka'])
                    v = vehicleById[bestdist[3]]
                    movements.insert(i+1, ['move.action = ActionType.CLEAR_AND_SELECT; move.left = ' + str(v.x - 5) + '; move.right = ' + str(v.x + 5) + '; move.top = ' + str(v.y - 5) + '; move.bottom = ' + str(v.y + 5), 2, 'nuka'])
                    k = (maxDist[v.type] - bestdist[2]) / maxDist[v.type]
                    movements.insert(i+2, ['move.action = ActionType.MOVE; move.x, move.y = '+ str((v.x - bestdist[0]) * k)+', ' + str((v.y - bestdist[1]) * k ), 1, 'nuka'])

        #Если очков мало
        if ((me.score-enemy.score) < (20001-wti)/50) & (me.remaining_nuclear_strike_cooldown_ticks == 0) & (wti % 300 == 0) & (wti > 300):
            myFly = []
            for i in myVehicleIds:
                v=vehicleById[i]
                if (v.type == VehicleType.FIGHTER) | (v.type == VehicleType.HELICOPTER):
                    myFly.append(vehicleById[i])
            enemyArmy = []
            for i in enemyVehicleIds:
                v=vehicleById[i]
                if v.type != VehicleType.ARRV:
                    enemyArmy.append(vehicleById[i])
            distMin = 10000
            distEnemy = 10000
            for v in myFly:
                dist=v.get_distance_to(1023, 1023)
                if dist < distMin:
                    distMin = dist
                    distMinI = v.id
            if distMin !=10000:
                myV = vehicleById[distMinI]
                for v in enemyArmy:
                    dist=v.get_distance_to(myV.x, myV.y)
                    if dist < distEnemy:
                        distEnemy = dist
                        distEnemyI = v.id
                if enemyArmy:
                    enV = vehicleById[distEnemyI]
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left = ' + str(myV.x - 5) + '; move.right = ' + str(myV.x + 5) + '; move.top = ' + str(myV.y - 5) + '; move.bottom = ' + str(myV.y + 5), 0, 'scout'])
                    b = myV.get_distance_to(enV.x, enV.y)
                    k = (b - minDist[myV.type]) / b
                    movements.append(['move.action = ActionType.MOVE; move.x, move.y = '+ str((enV.x - myV.x) * k) + ', ' + str((enV.y - myV.y) * k), 1, 'scout']) 
                else:
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left = ' + str(myV.x - 5) + '; move.right = ' + str(myV.x + 5) + '; move.top = ' + str(myV.y - 5) + '; move.bottom = ' + str(myV.y + 5), 0, 'scout'])
                    b = myV.get_distance_to(900, 900)
                    k = (b - minDist[myV.type]) / b
                    movements.append(['move.action = ActionType.MOVE; move.x, move.y = '+ str((900 - myV.x) * k) + ', ' + str((900 - myV.y) * k), 1, 'scout']) 

        #Фабрики
        if (wti % 30 == 0):
            if world.facilities:
                for f in world.facilities:
                    if (f.type == FacilityType.VEHICLE_FACTORY) & (f.owner_player_id == me.id):
                        if (f.vehicle_type is None):
                            movements.append(['move.action = ActionType.SETUP_VEHICLE_PRODUCTION; move.facility_id = '+ str(f.id) + '; move.vehicle_type = ' + str(VehicleType.IFV), 0, 'factory_set'])
                        elif (f.vehicle_type in [ VehicleType.IFV, VehicleType.ARRV, VehicleType.TANK ]):
                            ground = myVehicleIdsByType[VehicleType.IFV] + myVehicleIdsByType[VehicleType.TANK] + myVehicleIdsByType[VehicleType.ARRV]
                            sumG = {}
                            for i in [ VehicleType.IFV, VehicleType.ARRV, VehicleType.TANK ]:
                                sumG[i] = 0
                                for j in myVehicleIdsByType[i]:
                                    v = vehicleById[j]
                                    if (v.x >= f.left) & (v.y >= f.top) & (v.x <= f.left + 64) & (v.y <= f.top + 64):
                                        sumG[i]+=1
                            if (sumG[VehicleType.IFV] + sumG[VehicleType.ARRV] + sumG[VehicleType.TANK]) > 65:
                                movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left = ' + str(f.left - 20) + '; move.right = ' + str(f.left + 84) + '; move.top = ' + str(f.top - 20) + '; move.bottom = ' + str(f.top + 84), 0, 'factory_ground'])
                                movements.append(['move.action = ActionType.SCALE; move.factor = 0.5; move.x, move.y = '+ str(f.left + 32) + ', ' + str(f.top + 32), 2, 'factory_ground']) 
                                maxGroup += 1
                                movements.append(['move.action = ActionType.ASSIGN; move.group = ' + str(maxGroup),1,'factory_ground'])
                                if len(myVehicleIdsByType[VehicleType.FIGHTER]) < len(enemyVehicleIdsByType[VehicleType.FIGHTER]):
                                    movements.append(['move.action = ActionType.SETUP_VEHICLE_PRODUCTION; move.facility_id = '+ str(f.id) + '; move.vehicle_type = ' + str(VehicleType.FIGHTER), 0, 'factory_set'])
                                else:
                                    movements.append(['move.action = ActionType.SETUP_VEHICLE_PRODUCTION; move.facility_id = '+ str(f.id) + '; move.vehicle_type = ' + str(VehicleType.HELICOPTER), 0, 'factory_set'])
                            else:
                                if (sumG[VehicleType.IFV] + sumG[VehicleType.ARRV] + sumG[VehicleType.TANK]) > 9:
                                    if (sumG[VehicleType.IFV] % 10 == 0) & (sumG[VehicleType.IFV] > sumG[VehicleType.ARRV]) & (sumG[VehicleType.IFV] > sumG[VehicleType.TANK]) & (f.vehicle_type == VehicleType.IFV):
                                        movements.append(['move.action = ActionType.SETUP_VEHICLE_PRODUCTION; move.facility_id = '+ str(f.id) + '; move.vehicle_type = ' + str(VehicleType.ARRV), 0, 'factory_set'])
                                    elif (sumG[VehicleType.ARRV] % 3 == 0) & (sumG[VehicleType.ARRV] >= sumG[VehicleType.IFV]//3) & (sumG[VehicleType.ARRV] > sumG[VehicleType.TANK]//3) & (f.vehicle_type == VehicleType.ARRV):
                                        movements.append(['move.action = ActionType.SETUP_VEHICLE_PRODUCTION; move.facility_id = '+ str(f.id) + '; move.vehicle_type = ' + str(VehicleType.TANK), 0, 'factory_set'])
                                    elif (sumG[VehicleType.TANK] % 10 == 0) & (sumG[VehicleType.TANK] >= sumG[VehicleType.IFV]) & (sumG[VehicleType.TANK] >= sumG[VehicleType.ARRV]) & (f.vehicle_type == VehicleType.TANK):
                                        movements.append(['move.action = ActionType.SETUP_VEHICLE_PRODUCTION; move.facility_id = '+ str(f.id) + '; move.vehicle_type = ' + str(VehicleType.IFV), 0, 'factory_set'])

                        elif (f.vehicle_type in [VehicleType.HELICOPTER, VehicleType.FIGHTER] ):
                            air = myVehicleIdsByType[VehicleType.FIGHTER] + myVehicleIdsByType[VehicleType.HELICOPTER] + myVehicleIdsByType[VehicleType.ARRV]
                            sumA = 0
                            for i in air:
                                v = vehicleById[i]
                                if (v.x >= f.left) & (v.y >= f.top) & (v.x <= f.left + 64) & (v.y <= f.top + 64):
                                    sumA+=1
                            if sumA >= 5:
                                movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.vehicle_type = '+ str(f.vehicle_type) + '; move.left = ' + str(f.left - 20) + '; move.right = ' + str(f.left + 84) + '; move.top = ' + str(f.top - 20) + '; move.bottom = ' + str(f.top + 84), 0, 'factory_air'])
                                movements.append(['move.action = ActionType.SCALE; move.factor = 2; move.x, move.y = '+ str(f.left + 32) + ', ' + str(f.top + 32), 2, 'factory_air']) 
                                maxGroup += 1
                                movements.append(['move.action = ActionType.ASSIGN; move.group = ' + str(maxGroup),1,'factory_air'])
                                movements.append(['move.action = ActionType.SETUP_VEHICLE_PRODUCTION; move.facility_id = '+ str(f.id) + '; move.vehicle_type = ' + str(VehicleType.IFV), 0, 'factory_set'])
        if round2:
            if (wti >= (min(len(facilityById),len(muNA))+1)*60):
                if (wti % ((maxGroup - len(deadGroups)+1)*20) == 0):
                    for i in range(1,maxGroup+1):
                        if i not in deadGroups:
                            cGX = []
                            cGY = []
                            for j in myVehicleIds:
                                v = vehicleById[j]
                                if i in v.groups:
                                    cGX.append(v.x)
                                    cGY.append(v.y)
                            if len(cGX) > 5:
                                centerGroups[i] = [np.median(cGX),np.median(cGY)]
                elif (wti % ((maxGroup - len(deadGroups)+1)*20) == 2):
                    newCenterGroups = {}
                    i = 0
                    while len(movements)>i:    
                        if (movements[i][2] == 'stuck') & (movements[i][1] == 0):
                            movements.pop(i)
                            movements.pop(i)
                        else:
                            i+=1
                    for i in range(1,maxGroup+1):
                        if (i not in deadGroups)&(i in centerGroups):
                            cGX = []
                            cGY = []
                            for j in myVehicleIds:
                                v = vehicleById[j]
                                if i in v.groups:
                                    cGX.append(v.x)
                                    cGY.append(v.y)
                            if len(cGX) > 3:
                                if len(cGX) < 6:
                                    movements.append(['move.action = ActionType.DISBAND; move.group = ' + str(i), 0, 'disband'])
                                    deadGroups.append(i)
                                else:
                                    newCenterGroups[i] = [np.median(cGX),np.median(cGY)]
                                    if ((newCenterGroups[i][0] - centerGroups[i][0])**2 + (newCenterGroups[i][1] - centerGroups[i][1])**2 < 0.02) | ((wti>3000)&(wti%1000 > 0)&(wti%1000 <= ((maxGroup - len(deadGroups) + 1 )*20) + 1 )):
                                        stopFlag = True
                                        for f in world.facilities:
                                            if ((f.owner_player_id!=me.id)|(f.capture_points < game.max_facility_capture_points)) & ((newCenterGroups[i][0] >= f.left - 10) & (newCenterGroups[i][1] >= f.top - 10) & (newCenterGroups[i][0] <= f.left + 74) & (newCenterGroups[i][1] <= f.top + 74)):
                                                stopFlag = False
                                        if stopFlag:
                                            #Новая цель
                                            minDistOccup = 10000000
                                            ind = -1
                                            for f in world.facilities:
                                                if (f.owner_player_id!=me.id)|(f.capture_points < game.max_facility_capture_points): #if (f.owner_player_id!=me.id)|(f.capture_points < game.max_facility_capture_points):
                                                    dist=(f.left + 32 - newCenterGroups[i][0])**2 + (f.top + 32 - newCenterGroups[i][1])**2 
                                                    if f.type == FacilityType.VEHICLE_FACTORY:
                                                        dist-=10000
                                                    if dist < minDistOccup:
                                                        minDistOccup = dist
                                                        ind = f.id
                                            if ind !=-1:
                                                f=facilityById[ind]
                                                movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = ' + str(min(cGX) - 3) + ', ' + str(max(cGX) + 3) + ', ' + str(min(cGY) - 3) + ', ' + str(max(cGY) + 3), 0, 'stuck'])
                                                movements.append(['move.action = ActionType.MOVE; move.x, move.y = '+ str(f.left + 32 - newCenterGroups[i][0]) + ', ' + str(f.top + 32 - newCenterGroups[i][1]), 1, 'stuck']) 
                                            elif (wti>13000):
                                                movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = ' + str(min(cGX) - 3) + ', ' + str(max(cGX) + 3) + ', ' + str(min(cGY) - 3) + ', ' + str(max(cGY) + 3), 0, 'stuck'])
                                                movements.append(['move.action = ActionType.MOVE; move.x, move.y = '+ str(mu[0][0] - newCenterGroups[i][0]) + ', ' + str(mu[1][0] - newCenterGroups[i][1]), 1, 'stuck'])
                            else:
                                deadGroups.append(i)

        #Убегаем
        if (wti > lastNukaTick + 30) & (wti % 60 == 30) & (minefield==False):
            kScale = K
            mu = []
            X = [[vehicleById[i].x, vehicleById[i].y] for i in enemyVehicleIds]
            if len(X) < kScale:
                kScale = len(X)
            if kScale != 0:
                mu = kmeans(X, kScale)[0]
                clustersX = [[],[],[],[],[]]
                clustersY = [[],[],[],[],[]]
                for i in range(0, len(X)):
                    distFromCenters = []
                    for center in mu:
                        distFromCenters.append((X[i][0] - center[0])**2 + (X[i][1] - center[1])**2)
                    ind = distFromCenters.index(min(distFromCenters))
                    clustersX[ind].append(X[i][0])
                    clustersY[ind].append(X[i][1])
                i = 0
                while len(movements)>i:    
                        if (movements[i][2] == 'scale')&(movements[i][1] == 0):
                            movements.pop(i)
                            movements.pop(i)
                        else:
                            i+=1
                aggrFlag = False
                for i in range(0, len(mu)):
                    minEnX=min(clustersX[i])
                    maxEnX=max(clustersX[i])
                    minEnY=min(clustersY[i])
                    maxEnY=max(clustersY[i])
                    sumMy=0
                    sumFac=0
                    nearestGroups= {}
                    notInGroups = 0
                    for gr in range(1,maxGroup+2):
                        nearestGroups[gr]=0
                    myAttack = 0
                    enAttack = 0
                    mySide = dict([(VehicleType.TANK, 0), (VehicleType.IFV, 0), (VehicleType.HELICOPTER, 0), (VehicleType.FIGHTER, 0), (VehicleType.ARRV, 0)])
                    enSide = dict([(VehicleType.TANK, 0), (VehicleType.IFV, 0), (VehicleType.HELICOPTER, 0), (VehicleType.FIGHTER, 0), (VehicleType.ARRV, 0)])
                    for j in myVehicleIds:
                        v=vehicleById[j]
                        if (v.x > minEnX - frame) & (v.x < minEnX + frame) & (v.y > minEnY - frame) & (v.y < minEnY + frame):
                            sumMy+=1
                            if v.groups:
                                for g in v.groups:
                                    nearestGroups[g]+=1
                            else:
                                notInGroups+=1
                    '''
                    if notInGroups > 0:
                        maxNearestGroup = 0
                        for g in nearestGroups:
                            mGV=max(nearestGroups.values())
                            if (nearestGroups[g] == mGV) & (mGV !=0):
                                maxNearestGroup = g
                        if maxNearestGroup == 0:
                            maxGroup+=1
                            maxNearestGroup=maxGroup
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left = ' + str(minEnX - frame) + '; move.right = ' + str(maxEnX + frame) + '; move.top = ' + str(minEnY - frame) + '; move.bottom = ' + str(maxEnY + frame), 0, 'scale'])
                        movements.append(['move.action = ActionType.ASSIGN; move.group = ' + str(maxNearestGroup),1,'scale'])
                        nearestGroups[maxNearestGroup] += notInGroups
                    '''
                    for j in myVehicleIds:
                        v=vehicleById[j]
                        if v.groups:
                            if (v.groups[0] in nearestGroups.keys()) & ((v.x > minEnX - frame) & (v.x < minEnX + frame) & (v.y > minEnY - frame) & (v.y < minEnY + frame)):
                                mySide[v.type]+=v.durability
                    for j in enemyVehicleIds:
                        v=vehicleById[j]
                        if (v.x > minEnX - frame) & (v.x < minEnX + frame) & (v.y > minEnY - frame) & (v.y < minEnY + frame):
                            enSide[v.type]+=v.durability
                    for j in range(0,5):
                        for k in range(0,5):
                            myAttack+=attacks[j][k] * (mySide[j]/100) - enSide[k]
                            enAttack+=attacks[j][k] * (enSide[j]/100) - mySide[k]

                    #for f in world.facilities:
                    #    if ( (f.top < minEnY - frame) | (f.top +64 > maxEnY + frame) | (f.left +64 < minEnX - frame) | (f.left > maxEnX + frame) ):
                    #        sumFac+=1
                    #        break

                    if ((wti>=15000)|((len(myVehicleIds)//2>len(enemyVehicleIds))&(game.fog_of_war_enabled == False))) & (round2) & (wti % 1000 <= 100):
                        aggrFlag = True
                    else:
                        if ((maxEnX - minEnX)!= 0) & ((maxEnY - minEnY) !=0):
                            if (sumMy>0) &(sumFac==0)& (((len(clustersX)/((maxEnX - minEnX) * (maxEnY - minEnY)))*10000) >2):
                                if (myAttack < enAttack):
                                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left = ' + str(minEnX - frame) + '; move.right = ' + str(maxEnX + frame) + '; move.top = ' + str(minEnY - frame) + '; move.bottom = ' + str(maxEnY + frame), 0, 'scale'])
                                    movements.append(['move.action = ActionType.SCALE; move.x, move.y = '+ str(mu[i][0]) + ', ' + str(mu[i][1]) + '; move.factor = ' + str(scaleFactor), 1, 'scale']) 
                                else:
                                    for g in nearestGroups.keys():
                                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.group = ' + str(g), 0, 'scale'])
                                        movements.append(['move.action = ActionType.SCALE; move.x, move.y = '+ str(mu[i][0]) + ', ' + str(mu[i][1]) + '; move.factor = 0.1', 1, 'scale']) 
                #Аггр мод - собираем 4 кучи и идем на 4 кластера врага
                if aggrFlag:
                    j = 0 
                    while len(movements)>j:    
                        if (movements[j][2] == 'stuck')&(movements[j][1] == 0):
                            movements.pop(j)
                            movements.pop(j)
                        else:
                            j+=1
                    j = 0
                    while len(movements)>j:    
                        if (movements[j][2] == 'scale')&(movements[j][1] == 0):
                            movements.pop(j)
                            movements.pop(j)
                        else:
                            j+=1
                    j = 0
                    while len(movements)>j:    
                        if (movements[j][2] == 'aggrMode')&(movements[j][1] == 0):
                            for k in range(0,18):
                                movements.pop(j)
                        else:
                            j+=1
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 0,511,0,511', 0, 'aggrMode'])
                    movements.append(['move.action = ActionType.SCALE; move.x, move.y = 256,511; move.factor = 0.1', 17, 'aggrMode']) 
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 512,1023,0,511', 16, 'aggrMode'])
                    movements.append(['move.action = ActionType.SCALE; move.x, move.y = 768,511; move.factor = 0.1', 15, 'aggrMode']) 
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 0,511,512,1023', 14, 'aggrMode'])
                    movements.append(['move.action = ActionType.SCALE; move.x, move.y = 256,512; move.factor = 0.1', 13, 'aggrMode']) 
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 512,1023,512,1023', 12, 'aggrMode'])
                    movements.append(['move.action = ActionType.SCALE; move.x, move.y = 768,512; move.factor = 0.1', 11, 'aggrMode']) 
                    movements.append(['pause',10,'aggrMode',100])
                    movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 0,511,0,511', 9, 'aggrMode'])
                    movements.append(['move.action = ActionType.SCALE; move.factor = 0.1; move.x, move.y = '+ str(mu[0][0]) + ', ' + str(mu[0][1]), 8, 'aggrMode']) 
                    if len(mu)>=2:
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 512,1023,0,511', 7, 'aggrMode'])
                        movements.append(['move.action = ActionType.SCALE; move.factor = 0.1; move.x, move.y = '+ str(mu[1][0]) + ', ' + str(mu[1][1]), 6, 'aggrMode'])
                    else:
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 512,1023,0,511', 7, 'aggrMode'])
                        movements.append(['move.action = ActionType.SCALE; move.factor = 0.1; move.x, move.y = '+ str(mu[0][0]) + ', ' + str(mu[0][1]), 6, 'aggrMode'])
                    if len(mu)>=3:
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 0,511,512,1023', 5, 'aggrMode'])
                        movements.append(['move.action = ActionType.SCALE; move.factor = 0.1; move.x, move.y = '+ str(mu[2][0]) + ', ' + str(mu[2][1]), 4, 'aggrMode']) 
                    else:
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 0,511,512,1023', 5, 'aggrMode'])
                        movements.append(['move.action = ActionType.SCALE; move.factor = 0.1; move.x, move.y = '+ str(mu[0][0]) + ', ' + str(mu[0][1]), 4, 'aggrMode']) 
                    if len(mu)>=4:
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 512,1023,512,1023', 3, 'aggrMode'])
                        movements.append(['move.action = ActionType.SCALE; move.factor = 0.1; move.x, move.y = '+ str(mu[3][0]) + ', ' + str(mu[3][1]), 2, 'aggrMode']) 
                    else:
                        movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.left, move.right, move.top, move.bottom = 512,1023,512,1023', 3, 'aggrMode'])
                        movements.append(['move.action = ActionType.SCALE; move.factor = 0.1; move.x, move.y = '+ str(mu[0][0]) + ', ' + str(mu[0][1]), 2, 'aggrMode']) 
                    movements.append(['pause',1,'aggrMode',600])       
        if (wti == 800) & (len(enemyVehicleIds)==0):
            movements.append(['move.action = ActionType.CLEAR_AND_SELECT; move.vehicle_type = VehicleType.FIGHTER; move.right = world.width; move.bottom = world.height',0,'total_scouts'])
            movements.append(['move.action = ActionType.SCALE; move.x, move.y = 512, 512; move.factor = 1.5',1,'total_scouts'])

        #Двигаемся
        if me.remaining_action_cooldown_ticks == 0:
            if movements:
                if movements[0][0] == 'pause':
                    movements[0][3] -= 1
                    if movements[0][3]<=1:
                        movements.pop(0)
                else:
                    exec(movements.pop(0)[0])