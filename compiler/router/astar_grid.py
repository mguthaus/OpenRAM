from itertools import tee
import debug
from vector3d import vector3d
import grid
from heapq import heappush,heappop

class astar_grid(grid.grid):
    """
    Expand the two layer grid to include A* search functions for a source and target.
    """

    def __init__(self):
        """ Create a routing map of width x height cells and 2 in the z-axis. """
        grid.grid.__init__(self)
        
        # list of the source/target grid coordinates
        self.source = []
        self.target = []

        # priority queue for the maze routing
        self.q = []

    def set_source(self,n):
        self.add_map(n)
        self.map[n].source=True
        self.source.append(n)
        
    def set_target(self,n):
        self.add_map(n)
        self.map[n].target=True
        self.target.append(n)

        
    def add_source(self,track_list):
        debug.info(2,"Adding source list={0}".format(str(track_list)))
        for n in track_list:
            if not self.is_blocked(n):
                debug.info(3,"Adding source ={0}".format(str(n)))
                self.set_source(n)

    def add_target(self,track_list):
        debug.info(2,"Adding target list={0}".format(str(track_list)))
        for n in track_list:
            if not self.is_blocked(n):
                self.set_target(n)

    def is_target(self,point):
        """
        Point is in the target set, so we are done.
        """
        return point in self.target
            
    def reinit(self):
        """ Reinitialize everything for a new route. """

        # Reset all the cells in the map
        for p in self.map.values():
            p.reset()
        
        # clear source and target pins
        self.source=[]
        self.target=[]
        
        # Clear the queue 
        while len(self.q)>0:
            heappop(self.q)
        self.counter = 0

    def init_queue(self):
        """
        Populate the queue with all the source pins with cost
        to the target. Each item is a path of the grid cells.
        We will use an A* search, so this cost must be pessimistic.
        Cost so far will be the length of the path.
        """
        debug.info(4,"Initializing queue.")

        # uniquify the source (and target while we are at it)
        self.source = list(set(self.source))
        self.target = list(set(self.target))

        # Counter is used to not require data comparison in Python 3.x
        # Items will be returned in order they are added during cost ties
        self.counter = 0
        for s in self.source:
            cost = self.cost_to_target(s)
            debug.info(1,"Init: cost=" + str(cost) + " " + str([s]))
            heappush(self.q,(cost,self.counter,[s]))
            self.counter+=1

            
    def route(self,detour_scale):
        """
        This does the A* maze routing with preferred direction routing.
        """

        # We set a cost bound of the HPWL for run-time. This can be 
        # over-ridden if the route fails due to pruning a feasible solution.
        cost_bound = detour_scale*self.cost_to_target(self.source[0])*self.PREFERRED_COST

        # Make sure the queue is empty if we run another route
        while len(self.q)>0:
            heappop(self.q)

        # Put the source items into the queue
        self.init_queue()
        cheapest_path = None
        cheapest_cost = None
        
        # Keep expanding and adding to the priority queue until we are done
        while len(self.q)>0:
            # should we keep the path in the queue as well or just the final node?
            (cost,count,path) = heappop(self.q)
            debug.info(2,"Queue size: size=" + str(len(self.q)) + " " + str(cost))
            debug.info(3,"Expanding: cost=" + str(cost) + " " + str(path))
            
            # expand the last element
            neighbors =  self.expand_dirs(path)
            debug.info(3,"Neighbors: " + str(neighbors))
            
            for n in neighbors:
                # node is added to the map by the expand routine
                newpath = path + [n]
                # check if we hit the target and are done
                if self.is_target(n):
                    return (newpath,self.cost(newpath))
                elif not self.map[n].visited:
                    # current path cost + predicted cost
                    current_cost = self.cost(newpath)
                    target_cost = self.cost_to_target(n)                    
                    predicted_cost = current_cost +  target_cost
                    # only add the cost if it is less than our bound
                    if (predicted_cost < cost_bound):
                        if (self.map[n].min_cost==-1 or current_cost<self.map[n].min_cost):
                            self.map[n].visited=True
                            self.map[n].min_path = newpath
                            self.map[n].min_cost = predicted_cost
                            debug.info(3,"Enqueuing: cost=" + str(current_cost) + "+" + str(target_cost) + " " + str(newpath))
                            # add the cost to get to this point if we haven't reached it yet
                            heappush(self.q,(predicted_cost,self.counter,newpath))
                            self.counter += 1

        debug.warning("Unable to route path. Expand the detour_scale to allow detours.")
        return (None,None)

    def expand_dirs(self,path):
        """
        Expand each of the four cardinal directions plus up or down
        but not expanding to blocked cells. Expands in all directions
        regardless of preferred directions.
        """
        # expand from the last point
        point = path[-1]

        neighbors = []
        
        east = point + vector3d(1,0,0)
        if not self.is_blocked(east) and not east in path:                
            neighbors.append(east)
        
        west= point + vector3d(-1,0,0)
        if not self.is_blocked(west) and not west in path:                
            neighbors.append(west)

        up = point + vector3d(0,0,1)
        if up.z<2 and not self.is_blocked(up) and not up in path:
                neighbors.append(up)

        north = point + vector3d(0,1,0)
        if not self.is_blocked(north) and not north in path:                
            neighbors.append(north)

        south = point + vector3d(0,-1,0)
        if not self.is_blocked(south) and not south in path:                
            neighbors.append(south)
                
        down = point + vector3d(0,0,-1)
        if down.z>=0 and not self.is_blocked(down) and not down in path:
            neighbors.append(down)

        return neighbors


    def hpwl(self, src, dest):
        """ 
        Return half perimeter wire length from point to another.
        Either point can have positive or negative coordinates. 
        Include the via penalty if there is one.
        """
        hpwl = max(abs(src.x-dest.x),abs(dest.x-src.x))
        hpwl += max(abs(src.y-dest.y),abs(dest.y-src.y))
        hpwl += max(abs(src.z-dest.z),abs(dest.z-src.z))
        if src.x!=dest.x or src.y!=dest.y:
            hpwl += self.VIA_COST
        return hpwl
            
    def cost_to_target(self,source):
        """
        Find the cheapest HPWL distance to any target point ignoring 
        blockages for A* search.
        """
        cost = self.hpwl(source,self.target[0])
        for t in self.target:
            cost = min(self.hpwl(source,t),cost)
        return cost


    def cost(self,path):
        """ 
        The cost of the path is the length plus a penalty for the number
        of vias. We assume that non-preferred direction is penalized.
        """

        # Ignore the source pin layer change, FIXME?
        def pairwise(iterable):
            "s -> (s0,s1), (s1,s2), (s2, s3), ..."
            a, b = tee(iterable)
            next(b, None)
            return zip(a, b)


        plist = pairwise(path)
        cost = 0
        for p0,p1 in plist:
            if p0.z != p1.z: # via
                cost += self.VIA_COST
            elif p0.x != p1.x: # horizontal
                cost += self.NONPREFERRED_COST if (p0.z == 1) else self.PREFERRED_COST
            elif p0.y != p1.y: # vertical
                cost += self.NONPREFERRED_COST if (p0.z == 0) else self.PREFERRED_COST
            else:
                debug.error("Non-changing direction!")

        return cost
    
    def get_inertia(self,p0,p1):
        """ 
        Sets the direction based on the previous direction we came from. 
        """
        # direction (index) of movement
        if p0.x==p1.x:
            return 1
        elif p0.y==p1.y:
            return 0
        else:
            # z direction
            return 2

        
        
