"""
    I don't like filling the code with comments but there is no 
    better way to explain the idea behind each section

    Berkoztas - 25260
"""
import cv2
import time

"""
    First time i used classes seriously
    so there might be some mistakes or better ways :)
"""
class Maze:
    class Node:
        def __init__(self,pos):
            self.pos = pos
            self.neighbours = [None,None,None,None]
            #		    Up, Right, Down, Left

    def __init__(self,img):

        self.img = img
        self.rows = self.img.shape[0]
        self.columns = self.img.shape[1]
                
        print("\nThe image has {} pixels!!".format(self.rows*self.columns))

        self.count = 0 # To count the nodes

        self.timer = time.time()

        self.topnodes = {} #stolen idea

        n = None # For storing the last node

        print("\nCreating and connecting nodes...")
        
        # Top node
        for i in range(self.columns):
            if self.img[0][i] == 255:
                n = Maze.Node((0,i))
                self.start_node = n
                self.topnodes[i] = n
                self.count += 1

        for i in range(1, self.rows-1):

            prv = False
            cur = self.img[i][0] == 255
            nxt = self.img[i][1] == 255

            leftnode = None

            for j in range(1,self.columns-1):

                prv = cur
                cur = nxt
                nxt = self.img[i][j+1] == 255

                n = None

                if cur == False:
                    # On wall
                    continue

                if prv == True:

                    if nxt == True:
                        # PATH PATH PATH
                        # Create nodes only if path above or below
                        if (self.img[i+1][j] == 255) or (self.img[i-1][j] == 255):
                            n = Maze.Node((i,j))
                            leftnode.neighbours[1] = n
                            n.neighbours[3] = leftnode
                            leftnode = n

                    else:
                        # PATH PATH WALL
                        # End of corridor
                        n = Maze.Node((i,j))
                        leftnode.neighbours[1] = n
                        n.neighbours[3] = leftnode
                        leftnode = None

                else:

                    if nxt == True:
                        # WALL PATH PATH
                        n = Maze.Node((i,j))
                        leftnode = n

                    else:
                        # WALL PATH WALL
                        # Only if dead end
                        if (self.img[i+1][j] == 0) or (self.img[i-1][j] == 0):
                                n = Maze.Node((i,j))

                if n != None :
                    self.count += 1
                    # if clear above
                    if self.img[i-1][j] == 255:
                        t = self.topnodes[j]
                        t.neighbours[0] = n
                        n.neighbours[2] = t

                    # if clear below
                    if self.img[i+1][j] == 255:
                        self.topnodes[j] = n

                    else:
                        self.topnodes[j] = None
            
        # Bottom node
        for i in range(self.columns):
            if img[self.rows-1][i] == 255:
                n = Maze.Node(((self.rows-1),i))
                self.end_node = n
                t = self.topnodes[i]
                t.neighbours[2] = n
                n.neighbours[0] = t
                self.count += 1

        print("\nDone, {} nodes have been created".format(self.count))

    
    def solve(self, alg):

        """
            This function holds necessary variables for algorithms
            And also gives the output
            I run the solving algorithm from here because this way
            its easier to add new algorthms
        """
        self.queue = {} # To choose the shortest yet
        self.from_dict = {} # Record of my movement through nodes
        self.visited = [] # Visited nodes

        self.queue[self.start_node] = 0

        self.path = [] # This variable is the final path
        self.Finished = False 

        if alg == "spacefill":
            Maze.spacefill(self)
        elif alg == "df":
            Maze.depthFirst(self)

        print("\nPreparing the image...")

        #Change the color channel to paint it red
        self.img = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        
        """
            This piece of code looks complicated but
            the idea was simple :D
            Takes two sequential nodes from the final path
            either x or y values should be same
            takes the distance between them
            and paints every pixel between them
        """
        for i in range(len(self.path)):

            if (i != len(self.path)-1): # if not the last node
                node_1 = self.path[i]
                node_2 = self.path[i+1]

                if (node_1.pos[0] == node_2.pos[0]): # if they are in the same row
                    big = max(node_1.pos[1],node_2.pos[1]) # value of big column
                    small = min(node_1.pos[1],node_2.pos[1]) # valaue of small column

                    for j in range(small, big+1): # from small to big
                        self.img[node_1.pos[0],j] = [0,0,255] # rows are same

                elif (node_1.pos[1] == node_2.pos[1]): # same as above but vertical neighbours
                    big = max(node_1.pos[0],node_2.pos[0])
                    small = min(node_1.pos[0],node_2.pos[0])

                    for j in range(small, big+1):
                        self.img[j,node_1.pos[1]] = [0,0,255]

        cv2.imwrite("solved3.png", self.img) #Writes the final image

        print("\nDone!")

        print("\nIt took {} seconds.".format(round((time.time()-self.timer),4)))

        input("\nPress enter to exit.")

    def depthFirst(self):

        print("\nSolving...")

        while not self.Finished:

##            selected = max([i for i in self.queue.values() if float(i).is_integer()])
            selected = min(self.queue.values())

            for i in self.queue.keys():
                if self.queue[i] == selected:
                    selected = i
                    break

            if selected == self.end_node:
                nextnode = self.end_node
                while True:
                    self.path.insert(0,nextnode)
                    if nextnode == self.start_node:
                        break
                    nextnode = self.from_dict[nextnode]
                
                self.Finished = True

                break

            for node in selected.neighbours:
                if node != None:
                    if node not in self.visited:
                        self.queue[node] = self.queue[selected] - 1
                        self.from_dict[node] = selected

            self.visited.append(selected)

            del self.queue[selected]
            
##            print("\nVisited {}/{} nodes".format(len(self.visited),self.count))

    def spacefill(self):

        print("\nSolving...")

        while not self.Finished:

##            selected = max([i for i in self.queue.values() if float(i).is_integer()])
            selected = min(self.queue.values())

            for i in self.queue.keys():
                if self.queue[i] == selected:
                    selected = i
                    break

            if selected == self.end_node:
                nextnode = self.end_node
                while True:
                    self.path.insert(0,nextnode)
                    if nextnode == self.start_node:
                        break
                    nextnode = self.from_dict[nextnode]
                
                self.Finished = True

                break

            for node in selected.neighbours:
                if node != None:
                    if node not in self.visited:
                        self.queue[node] = self.queue[selected] + 1
                        self.from_dict[node] = selected

            self.visited.append(selected)

            del self.queue[selected]

##            print("\nVisited {}/{} nodes".format(len(self.visited),self.count))

        print("\nSolved.")

    def show(self):
        cv2.imshow("test", self.img)
##        print(self.img)

"""
    Options for images from small to big (- dimentions):
    Mazes//tiny.png - 10x10
    Mazes//small.png - 15x15
    Mazes//normal.png - 41x41
    Mazes//braid200.png - 201x201
    Mazes//combo400.png - 401x401
    Mazes//braid2k.png - 2001x1940 < This takes an insane amount of time
    Mazes//perfect2k.png - 2001x2001 < All the others below too of course
    Mazes//perfect4k.png - 4001x4001
    Mazes//combo6k.png - 6001x6001
    Mazes//perfect10k.png - 10001x10001
    Mazes//perfect15k.png - 15001x15001

"""

if __name__ == '__main__':
    
    img = cv2.imread("Mazes//perfect4k.png", 0)

    maze = Maze(img) # initialize the nodes and connections

    maze.solve("df") # solve


