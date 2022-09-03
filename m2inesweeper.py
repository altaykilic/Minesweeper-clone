import os, sys, random, tkinter
try:
	import pygame
except Exception:
	os.system("python -m pip install pygame")
	import pygame
	
import menu

pygame.init()
sys.setrecursionlimit(10**6)

#constants
with open("comms.txt", "r") as filename:
	lst = filename.read().split()
	#bunlar pixel değil kare sayısı cinsinden
	BOARD_WIDTH = int(lst[0])
	BOARD_HEIGHT = int(lst[1])
	MINES = int(lst[2])
TILE_SIZE = 20
DISPLAY_SIZE = 40
FPS = 60
RESET_BUTTON = 120
WINDOW_HEIGHT = BOARD_HEIGHT*TILE_SIZE + DISPLAY_SIZE
if BOARD_WIDTH*TILE_SIZE <= 400:
	WINDOW_WIDTH = 400
	OFFSET = int((WINDOW_WIDTH-BOARD_WIDTH*TILE_SIZE)/2)
else:
	WINDOW_WIDTH = BOARD_WIDTH*TILE_SIZE
	OFFSET = 0
FACEPOSX = WINDOW_WIDTH/2-15

#assets
tileempty = pygame.image.load(os.path.join('assets','empty.png'))
tiles = [pygame.image.load(os.path.join('assets','0.png')), pygame.image.load(os.path.join('assets','1.png')), pygame.image.load(os.path.join('assets','2.png')), pygame.image.load(os.path.join('assets','3.png')), pygame.image.load(os.path.join('assets','4.png')), pygame.image.load(os.path.join('assets','5.png')), pygame.image.load(os.path.join('assets','6.png')), pygame.image.load(os.path.join('assets','7.png')), pygame.image.load(os.path.join('assets','8.png'))]
tileflag = pygame.image.load(os.path.join('assets','flag.png'))
tileredflag = pygame.image.load(os.path.join('assets','redflag.png'))
tileredmine = pygame.image.load(os.path.join('assets','minered.png'))
tilemine = pygame.image.load(os.path.join('assets','mine.png'))
explodesfx = pygame.mixer.Sound(os.path.join('assets','mine_explode.mp3'))
facebg0 = pygame.image.load(os.path.join('assets','facebg0.png'))
facebg1 = pygame.image.load(os.path.join('assets','facebg1.png'))
face0 = pygame.image.load(os.path.join('assets','face0.png'))
face1 = pygame.image.load(os.path.join('assets','face1.png'))
face2 = pygame.image.load(os.path.join('assets','face2.png'))
face3 = pygame.image.load(os.path.join('assets','face3.png'))
cursorind = pygame.image.load(os.path.join('assets','cursor2.png'))
numbers = [pygame.image.load(os.path.join('assets','number0.png')), pygame.image.load(os.path.join('assets','number1.png')), pygame.image.load(os.path.join('assets','number2.png')), pygame.image.load(os.path.join('assets','number3.png')), pygame.image.load(os.path.join('assets','number4.png')), pygame.image.load(os.path.join('assets','number5.png')), pygame.image.load(os.path.join('assets','number6.png')), pygame.image.load(os.path.join('assets','number7.png')), pygame.image.load(os.path.join('assets','number8.png')), pygame.image.load(os.path.join('assets','number9.png')), pygame.image.load(os.path.join('assets','colon0.png')), pygame.image.load(os.path.join('assets','colon1.png'))]

#custom events
TIMEREVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMEREVENT, 1000)
TIMERTICK = pygame.USEREVENT + 2
pygame.time.set_timer(TIMERTICK, 500)

#sumthing
timertick = 0

class Tile:
	#value negatifse mayın var
	#shown: 0->kapalı, 1->açık, 2->flag
	def __init__(self, val=0, shown=0):
		self.val = val
		self.shown = shown
	
	def display(self):
		if self.shown == 0:
			return tileempty
		elif self.shown == 2:
			return tileflag
		elif self.shown == 3:
			return tileredflag
		elif self.shown == 4:
			return tileredmine
		elif self.val < 0:
			return tilemine
		else:
			return tiles[self.val]

board = [[Tile(0,0) for x in range(BOARD_HEIGHT)] for y in range(BOARD_WIDTH)]

#display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Minesweeper')

#utility function
def boardi(x: int, y: int) -> Tile:
	return board[x][y]

#utility function
#	(-1,-1) = nothing, (-1,0) = reset button
def mousepos() -> (int,int):
	pos = pygame.mouse.get_pos()
	if pos[0] < FACEPOSX+30 and pos[0] >= FACEPOSX and pos[1] < 35 and pos[1] >= 5:
		return (-1,0)
	if pos[0] > OFFSET and pos[0] < WINDOW_WIDTH-OFFSET and pos[1] < WINDOW_HEIGHT and pos[1] > DISPLAY_SIZE:
		return ((pos[0]-OFFSET)//TILE_SIZE, (pos[1]-DISPLAY_SIZE)//TILE_SIZE)
	return (-1,-1)

#	n: number, (x,y): position, length: minimum length
def blitnumber(n: int, x: int, y: int, length: int = 0) -> None:
	digits = []
	while n > 0:
		digits.append(n%10)
		n //= 10
	
	pos = (x,y)
	while length - len(digits) > 0:
		screen.blit(numbers[0], pos)
		pos = (pos[0]+17, pos[1])
		length -= 1
	
	for i in digits[::-1]:
		screen.blit(numbers[i], pos)
		pos = (pos[0]+17, pos[1])

def blitboard(tick: bool = 0, click: (int,int) = (-1,-1), cursor: (int,int) = (0,0), show_cursor: bool = 0) -> None:
	global gameend
	
	for itx in range(BOARD_WIDTH):
		for ity in range(BOARD_HEIGHT):
			screen.blit(board[itx][ity].display(), (itx*TILE_SIZE+OFFSET, ity*TILE_SIZE+DISPLAY_SIZE))
	
	if click[0] >= 0 and click[0] < BOARD_WIDTH and click[1] >= 0 and click[1] < BOARD_HEIGHT and boardi(*click).shown == 0:
		screen.blit(tiles[0], (click[0]*TILE_SIZE+OFFSET, click[1]*TILE_SIZE+DISPLAY_SIZE))
	
	if click == (-1,0):
		screen.blit(facebg1, (FACEPOSX,5))
	else:
		screen.blit(facebg0, (FACEPOSX,5))
	if gameend == 1:
		screen.blit(face2, (FACEPOSX, 5))
	elif gameend == 2:
		screen.blit(face3, (FACEPOSX, 5))
	elif click[0] == -1:
		screen.blit(face0, (FACEPOSX,5))
	else:
		screen.blit(face1, (FACEPOSX,5))
	
	if show_cursor and not gameend:
		screen.blit(cursorind, (cursor[0]*TILE_SIZE+OFFSET, cursor[1]*TILE_SIZE+DISPLAY_SIZE))
	
	blitnumber((timerval//3600)%100, 5, 5, 2)
	blitnumber((timerval//60)%60, 44, 5, 2)
	blitnumber(timerval%60, 83, 5, 2)
	screen.blit(numbers[11-tick], (39,5))
	screen.blit(numbers[11-tick], (78,5))
	
	blitnumber(MINES-flagged_tiles, WINDOW_WIDTH-5-17*len(str(MINES)), 5, len(str(MINES)))

#resets the game
def reset() -> None:
	global opened_tiles, flagged_tiles, nomoves, timerval, timertick, gameend, cursor
	opened_tiles = 0
	flagged_tiles = 0
	nomoves = 1
	timerval = 0
	gameend = 0
	cursor = (0,0)
	
	for itx in range(BOARD_WIDTH):
		for ity in range(BOARD_HEIGHT):
			board[itx][ity].val = 0
			board[itx][ity].shown = 0
	screen.fill((230,230,230))
	blitboard(timertick)
	
	pygame.display.flip()

def lose(x,y):
	global gameend
	
	explodesfx.play()
	gameend = 1
	
	for itx in range(BOARD_WIDTH):
		for ity in range(BOARD_HEIGHT):
			if board[itx][ity].shown == 0 and board[itx][ity].val < 0:
				board[itx][ity].shown = 1
			elif board[itx][ity].shown == 2 and board[itx][ity].val >= 0:
				board[itx][ity].shown = 3
	
	board[x][y].shown = 4

def win():
	global gameend
	
	gameend = 2
	
	for itx in range(BOARD_WIDTH):
		for ity in range(BOARD_HEIGHT):
			if board[itx][ity].val < 0:
				board[itx][ity].shown = 2

#left-clicking a tile
def move(x: int, y: int, dfs: bool = 0) -> None:
	global opened_tiles
	
	if board[x][y].shown == 1 and dfs == 0:
		cnt = 0
		if x>0 and board[x-1][y].shown==2:										cnt+=1
		if x>0 and y<BOARD_HEIGHT-1 and board[x-1][y+1].shown==2:				cnt+=1
		if y<BOARD_HEIGHT-1 and board[x][y+1].shown==2:							cnt+=1
		if x<BOARD_WIDTH-1 and y<BOARD_HEIGHT-1 and board[x+1][y+1].shown==2:	cnt+=1
		if x<BOARD_WIDTH-1 and board[x+1][y].shown==2:							cnt+=1
		if x<BOARD_WIDTH-1 and y>0 and board[x+1][y-1].shown==2:				cnt+=1
		if y>0 and board[x][y-1].shown==2:										cnt+=1
		if x>0 and y>0 and board[x-1][y-1].shown==2:							cnt+=1
		
		if cnt == board[x][y].val:
			if x>0 and board[x-1][y].val<0 and board[x-1][y].shown==0:										lose(x-1, y);	return
			if x>0 and y<BOARD_HEIGHT-1 and board[x-1][y+1].val<0 and board[x-1][y+1].shown==0:				lose(x-1, y+1);	return
			if y<BOARD_HEIGHT-1 and board[x][y+1].val<0 and board[x][y+1].shown==0:							lose(x,   y+1);	return
			if x<BOARD_WIDTH-1 and y<BOARD_HEIGHT-1 and board[x+1][y+1].val<0 and board[x+1][y+1].shown==0:	lose(x+1, y+1);	return
			if x<BOARD_WIDTH-1 and board[x+1][y].val<0 and board[x+1][y].shown==0:							lose(x+1, y);	return
			if x<BOARD_WIDTH-1 and y>0 and board[x+1][y-1].val<0 and board[x+1][y-1].shown==0:				lose(x+1, y-1);	return
			if y>0 and board[x][y-1].val<0 and board[x][y-1].shown==0:										lose(x,   y-1);	return
			if x>0 and y>0 and board[x-1][y-1].val<0 and board[x-1][y-1].shown==0:							lose(x-1, y-1);	return
			
			if x>0:										move(x-1, y,   1)
			if x>0 and y<BOARD_HEIGHT-1:				move(x-1, y+1, 1)
			if y<BOARD_HEIGHT-1:						move(x,   y+1, 1)
			if x<BOARD_WIDTH-1 and y<BOARD_HEIGHT-1:	move(x+1, y+1, 1)
			if x<BOARD_WIDTH-1:							move(x+1, y,   1)
			if x<BOARD_WIDTH-1 and y>0:					move(x+1, y-1, 1)
			if y>0:										move(x,   y-1, 1)
			if x>0 and y>0:								move(x-1, y-1, 1)
	
	if board[x][y].shown == 0:
		if board[x][y].val < 0:
			lose(x,y)
			return
		
		board[x][y].shown = 1
		opened_tiles += 1
		
		if board[x][y].val == 0:
			if x>0:										move(x-1, y,   1)
			if x>0 and y<BOARD_HEIGHT-1:				move(x-1, y+1, 1)
			if y<BOARD_HEIGHT-1:						move(x,   y+1, 1)
			if x<BOARD_WIDTH-1 and y<BOARD_HEIGHT-1:	move(x+1, y+1, 1)
			if x<BOARD_WIDTH-1:							move(x+1, y,   1)
			if x<BOARD_WIDTH-1 and y>0:					move(x+1, y-1, 1)
			if y>0:										move(x,   y-1, 1)
			if x>0 and y>0:								move(x-1, y-1, 1)

#left-clicking for the first time
#sets the mines
def firstmove(x: int, y: int) -> None:
	#remaining tiles and mines
	tilesrem = BOARD_WIDTH*BOARD_HEIGHT
	minesrem = MINES
	
	if (x==0 or x==BOARD_WIDTH-1) and (y==0 or y==BOARD_HEIGHT-1):
		tilesrem -= 4
	elif x==0 or x==BOARD_WIDTH-1 or y==0 or y==BOARD_HEIGHT-1:
		tilesrem -= 6
	else:
		tilesrem -= 9
	
	for itx in range(BOARD_WIDTH):
		for ity in range(BOARD_HEIGHT):
			if itx >= x-1 and itx <= x+1 and ity >= y-1 and ity <= y+1:
				continue
			
			if random.randint(0, tilesrem-1) < minesrem:
				minesrem -= 1
				board[itx][ity].val -= 9
				
				if itx>0:										board[itx-1][ity  ].val += 1
				if itx>0 and ity<BOARD_HEIGHT-1:				board[itx-1][ity+1].val += 1
				if ity<BOARD_HEIGHT-1:							board[itx  ][ity+1].val += 1
				if itx<BOARD_WIDTH-1 and ity<BOARD_HEIGHT-1:	board[itx+1][ity+1].val += 1
				if itx<BOARD_WIDTH-1:							board[itx+1][ity  ].val += 1
				if itx<BOARD_WIDTH-1 and ity>0:					board[itx+1][ity-1].val += 1
				if ity>0:										board[itx  ][ity-1].val += 1 
				if itx>0 and ity>0:								board[itx-1][ity-1].val += 1
			
			tilesrem -= 1
	
	move(x,y)

def main() -> None:
	global opened_tiles, flagged_tiles, nomoves, timerval, timertick, gameend, cursor
	
	clicking = (-1,-1)
	cursor = (0,0)
	show_cursor = 0
	
	reset()
	clock = pygame.time.Clock()
	while True:
		#Frames Per Second
		clock.tick(FPS)
		
		if opened_tiles == BOARD_WIDTH*BOARD_HEIGHT-MINES:
			win()
		
		blitboard(timertick, clicking, cursor, show_cursor)
		pygame.display.flip()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			
			elif event.type == TIMEREVENT and gameend == 0:
				timerval += 1
			
			elif event.type == TIMERTICK:
				timertick = not timertick
			
			elif event.type == pygame.MOUSEBUTTONDOWN:
				show_cursor = 0
				
				#something something
				#now only god knows
				
				if pygame.mouse.get_pressed(3)[0] + pygame.mouse.get_pressed(3)[2] > 1 or pygame.mouse.get_pressed(3)[1]:
					clicking = (-1,-1)
					continue
				
				if gameend:
					if pygame.mouse.get_pressed(3)[0]:
						clicking = mousepos()
					if clicking != (-1,0):
						clicking = (-1,-1)
					continue
				
				if pygame.mouse.get_pressed(3)[2]:
					pos = mousepos()
					if pos[0] == -1:
						continue
					if boardi(*pos).shown == 2:
						boardi(*pos).shown = 0
						flagged_tiles -= 1
					elif boardi(*pos).shown == 0 and flagged_tiles < MINES:
						boardi(*pos).shown = 2
						flagged_tiles += 1
					clicking = (-1,-1)
				
				if pygame.mouse.get_pressed(3)[0]:
					clicking = mousepos()
					if boardi(*clicking).shown == 1:
						move(*clicking)
						clicking = (-1,-1)
					if boardi(*clicking).shown == 2:
						clicking = (-1,-1)
			
			elif event.type == pygame.MOUSEBUTTONUP:
				if pygame.mouse.get_pressed(3)[0] or pygame.mouse.get_pressed(3)[1] or pygame.mouse.get_pressed(3)[2]:
					clicking = (-1,-1)
					continue
				if clicking == mousepos():
					if clicking == (-1,0):
						reset()
					elif clicking[0] == -1:
						continue
					elif nomoves:
						firstmove(*clicking)
						nomoves = 0
					else:
						move(*clicking)
				clicking = (-1,-1)
			
			elif event.type == pygame.KEYDOWN:
				if event.key == 48: #0
					reset()
				elif gameend:
					continue
								
				elif event.key == 106: #j
					if nomoves:
						firstmove(*cursor)
						nomoves = 0
					else:
						move(*cursor)
				
				elif event.key == 107: #k
					if boardi(*cursor).shown == 2:
						boardi(*cursor).shown = 0
						flagged_tiles -= 1
					elif boardi(*cursor).shown == 0 and flagged_tiles < MINES:
						boardi(*cursor).shown = 2
						flagged_tiles += 1
				
				elif show_cursor: #wasd
					if event.key == 119 and cursor[1] > 0:
						cursor = (cursor[0], cursor[1]-1)
					elif event.key == 97  and cursor[0] > 0:
						cursor = (cursor[0]-1, cursor[1])
					elif event.key == 115 and cursor[1] < BOARD_HEIGHT-1:
						cursor = (cursor[0], cursor[1]+1)
					elif event.key == 100 and cursor[0] < BOARD_WIDTH-1:
						cursor = (cursor[0]+1, cursor[1])
				
				show_cursor = 1

if __name__ == '__main__':
	main()
