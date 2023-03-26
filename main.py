import pygame
import copy
import time
from Dims import Dims

# from const.constants import WIDTH, HEIGHT
from const.constants import BROWN, WHITE, OUTLINE, BACKGROUND, PIECE_X_COLOR, PIECE_O_COLOR, MENU_BACKGROUND_COLOR, WINNER_TEXT

dims: Dims = Dims(6)        # inicijalne dimenzije, za iscrtavanje menija

pygame.init()

# Inicijalizacija py-game prozora koji se iscrtava korisniku:
WIN = pygame.display.set_mode((dims.WIDTH, dims.HEIGHT))
pygame.display.set_caption('BaseDNK - Domineering!')
font = pygame.font.Font('cascadiacode.ttf', 32)

FPS: int = 60
LETTER_ARRAY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def main(dims: Dims) -> None:

    run = True
    clock = pygame.time.Clock()
    player: bool
    move_counter: int = 0
    computer_move: bool = False

    # Rezultat inicijalizacije, tuple koji se sastoji redom od podataka:
    # da li je igrac X prvi na potezu?
    # koja je dimenzija tabele?
    # objekat koji cuva dimenzije koje se kasnije koriste prilikom crtanja, vezano za py-game;

    res: tuple[bool, int, Dims] = init_game(WIN, clock, dims)
    
    # Za slucaj da je korisnik prilikom inicijalizacije odustao od igre:
    if res == None:
        pygame.quit()

    player = res[0]     # da li X igra prvi?
    dims = res[2]       # Nove dimenzije za iscrtavanje, koje se racunaju na osnovu korisnickog unosa dimenzije tabele;

    # Kreiramo tabelu u memoriji i iscrtavamo praznu tabelu korisniku:
    board: list[list[str]] = create_board(res[1])   
    draw_board(WIN, dims)

    # Petlja koja traje za vreme trajanja igre:
    # Sluzi za unos poteza, pozivanje min-max algoritma onda kada je na redu racunar, promenu narednog igraca,
    # proveru da li je kraj igre i iscrtavanje postavljenih figura u korisnickom prikazu:
    while run:

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            # Za slucaj da igra covek, cekamo prvo da klikne negde:
            if event.type == pygame.MOUSEBUTTONDOWN and not computer_move:

                piece_set = False

                # Proveravamo da li je kliknuo na neko polje na ekranu ili negde van table:
                if not get_cell_pos(pygame.mouse.get_pos(), dims) == (None, None):
                    piece_set = set_figure(WIN, get_cell_pos(pygame.mouse.get_pos(), dims), player, move_counter, board, dims)
                if piece_set:

                    # Promena narednog igraca (min/max):
                    player = not player

                    # Povecanje brojaca poteza:
                    move_counter = move_counter + 1

                    # Provera da li smo dosli do kraja igre:
                    run = not is_end(player, board) 

                    # Promena narednog igraca (covek/racunar):
                    computer_move = not computer_move

                    # Specijalni slucaj da covek vise nema poteza, da se ne bi nakon izlaska iz ove if labele igrao i potez za racunar:
                    if not run:
                        break

    
            # Za slucaj da igra racunar, ne cekamo na nista
            if computer_move and run:

                # Odgovor min-max algoritma, u obliku tuple[table, heur, x_pos, y_pos]
                # gde je 
                # table - prikaz najboljeg stanja tabele za prosledjenog igraca
                # heur - izracunara heuristika za krajnje stanje tabele
                # x_pos - kolona u kojoj se nalazi pocetak figure
                # y_pos - vrsta u kojoj se nalazi pocetak figure

                max_move = None

                # Startujemo tajmer pre pokretanja min-max algoritma:
                st = time.time()

                # Pozivamo min-max algoritam i cuvamo rezultat u promenljivu:
                max_move = min_max(board, player, 3, res[1])
                
                # Duzina trajanja odabira poteza u sekundama:
                et = time.time()
                elapsed_time = et - st

                print('Computer move: ', max_move[2], max_move[3])
                print('Execution time: ', elapsed_time, 'secconds')

                # Postavljanje figure na dobijenu poziciju:
                # Postavljanje figure u tabeli u memoriji i iscrtavanje figure na korisnickom prikazu:
                piece_set = False
                piece_set = set_figure(WIN, (max_move[2], max_move[3]), player, move_counter, board, dims)

                # Promena narednog igraca (min/max)
                player = not player

                # Povecanje brojaca poteza
                move_counter = move_counter + 1
                
                # Provera da li smo dosli do kraja igre?
                run = not is_end(player, board)

                # Promena narednog igraca (covek/racunar)
                computer_move = not computer_move
                

        pygame.display.update()

    # Stampanje pobednika i kraj igre:
    winer = "Human" if computer_move else "Computer"

    pygame.draw.rect(WIN, MENU_BACKGROUND_COLOR, (2, dims.HEIGHT // 2 - dims.cell_size // 2, dims.WIDTH - 4, dims.cell_size), 0, 5)
    text = font.render("The winner is: " + winer, False, WINNER_TEXT, None)
    text_rect = text.get_rect()
    text_rect.center = (dims.WIDTH // 2, dims.HEIGHT // 2)
    WIN.blit(text, text_rect)

    pygame.display.update()

    # Igra se ne zatvara sama, vec moramo da kliknemo na X da bi se zatvorila
    # Implementirano cisto da bi se videlo neko vreme ko je pobednik, nije preko potreban deo koda;
    exit_loop = True
    while exit_loop:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_loop = False

    pygame.quit()

# Funkcija za odabir prvog igraca i dimenzije tabele tabele:
def init_game(win, clock, dims: Dims) -> tuple[bool, int, Dims] or None:

    win.fill(BACKGROUND)

    # Postavljanje default vrednosti koje ce se kasnije popuniti korisnickim unosom:
    first_player: bool = False
    board_size: int = 0
    quit_event: bool = False
    got_player: bool = False
    got_size: bool = False

    # Forma za odabir igraca:
    pygame.draw.rect(win, MENU_BACKGROUND_COLOR, (dims.WIDTH // 10, dims.HEIGHT // 8, (dims.WIDTH // 10 * 8), (dims.HEIGHT // 8 * 6)), 0, 5)
    
    text = font.render("First play?", False, OUTLINE, None)
    text_rect = text.get_rect()
    text_rect.center = (dims.WIDTH // 2, dims.HEIGHT // 4)
    win.blit(text, text_rect)

    # Dugme za odabir igraca X:
    x_text = font.render("X", False, OUTLINE, None)
    x_text_rect = x_text.get_rect()
    pygame.draw.rect(win, PIECE_O_COLOR, (dims.WIDTH // 2 - 2 * dims.cell_size, dims.HEIGHT // 2 + dims.cell_size, dims.cell_size, dims.cell_size), 0, 5)
    x_text_rect.center = (dims.WIDTH // 2 - 2 * dims.cell_size + dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size + dims.cell_size // 2)
    win.blit(x_text, x_text_rect)

    
    # Dugme za odabir igraca Y:
    o_text = font.render("O", False, OUTLINE, None)
    o_text_rect = o_text.get_rect()
    pygame.draw.rect(win, PIECE_X_COLOR, (dims.WIDTH // 2 +  dims.cell_size, dims.HEIGHT // 2 + dims.cell_size, dims.cell_size, dims.cell_size), 0, 5)
    o_text_rect.center = (dims.WIDTH // 2 + dims.cell_size + dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size + dims.cell_size // 2)
    win.blit(o_text, o_text_rect)

    # Ispitivanje korisnickog unosa ko je prvi igrac, X ili Y:
    while not got_player:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_event = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Da li je kliknuto na X?
                if (pos[0] >= dims.WIDTH // 2 - 2 * dims.cell_size and pos[0] <= dims.WIDTH // 2 - dims.cell_size and pos[1] >= dims.HEIGHT // 2 + dims.cell_size and pos[1] <= dims.HEIGHT // 2 + 2 * dims.cell_size):
                    print('X selected!')
                    first_player = True
                    got_player = True

                elif (pos[0] >= dims.WIDTH // 2 + dims.cell_size and pos[0] <= dims.WIDTH // 2 + 2 * dims.cell_size and pos[1] >= dims.HEIGHT // 2 + dims.cell_size and pos[1] <= dims.HEIGHT // 2 + 2 * dims.cell_size):
                    print('Y selected!')
                    first_player = False
                    got_player = True

        pygame.display.update()
    
    
    # Brisanje prvog menija, odnosno, crtamo pozadinu preko svega, ne postoji stvar kao sto je
    # Brisanje nacrtanih elementa u pygame
    win.fill(BACKGROUND)

    # Sad trazimo unos velicine tabele:
    # Ako smo kliknuli na dugme za zatvaranje prozora, ne proveravamo dalje!
    if quit_event:
        return None
    
    # Forma za unos velicine tabele:
    pygame.draw.rect(win, MENU_BACKGROUND_COLOR, (dims.WIDTH // 10, dims.HEIGHT // 8, (dims.WIDTH // 10 * 8), (dims.HEIGHT // 8 * 6)), 0, 5)
    
    text = font.render("Table size?", False, OUTLINE, None)
    text_rect = text.get_rect()
    text_rect.center = (dims.WIDTH // 2, dims.HEIGHT // 4)
    win.blit(text, text_rect)


    # Rect za ispis unete velicine:
    # Ispis velicine moramo da uradimo unutar while petlje, jer moze da se desi da je dvocifrena, pa moramo da osvezimo prikaz:
    # Unutar ovog kvadrata ispisujemo velicinu:
    pygame.draw.rect(win, PIECE_X_COLOR, (dims.WIDTH // 2 - 2 * dims.cell_size - dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size, 2 * dims.cell_size, dims.cell_size), 0, 5)

    # Dugme za potvrdu velicine:
    text = font.render("Play!", False, OUTLINE, None)
    text_rect = text.get_rect()
    pygame.draw.rect(win, PIECE_O_COLOR, (dims.WIDTH // 2 + dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size, 2 * dims.cell_size, dims.cell_size), 0, 5)
    text_rect.center = (dims.WIDTH // 2 + dims.cell_size + dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size + dims.cell_size // 2)
    win.blit(text, text_rect)

    # Pomocna promenljiva, za ispitivanje zasto smo izasli iz petlje:
    quit_event = False

    # Ispitivanje korisnickog unosa dimenzije tabele (moze misem i klikom na enter):
    while not got_size:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                got_size = True
                quit_event = True
            
            elif event.type == pygame.KEYDOWN:
                if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                    board_size = board_size * 10 + (event.key - 48)     # pygame ne vraca koje dugme je konkretno kliknuto, vec stanje svih, tako da moramo ovako da proverimo koji je broj, 48 je sifra za 0:
                    
                    pygame.draw.rect(win, PIECE_X_COLOR, (dims.WIDTH // 2 - 2 * dims.cell_size - dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size, 2 * dims.cell_size, dims.cell_size), 0, 5)
                    size = font.render(str(board_size), False, OUTLINE, None)
                    size_rect = size.get_rect()
                    size_rect.center = (dims.WIDTH // 2 - 2 * dims.cell_size + dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size + dims.cell_size // 2)
                    win.blit(size, size_rect)

                elif event.key == pygame.K_BACKSPACE:
                    board_size = board_size // 10

                    pygame.draw.rect(win, PIECE_X_COLOR, (dims.WIDTH // 2 - 2 * dims.cell_size - dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size, 2 * dims.cell_size, dims.cell_size), 0, 5)
                    size = font.render(str(board_size), False, OUTLINE, None)
                    size_rect = size.get_rect()
                    size_rect.center = (dims.WIDTH // 2 - 2 * dims.cell_size + dims.cell_size // 2, dims.HEIGHT // 2 + dims.cell_size + dims.cell_size // 2)
                    win.blit(size, size_rect)

                # Ako je pritiskom na enter korisnik potvrdio pocetak igre:
                elif event.key == pygame.K_RETURN:
                    got_size = True
            
            # Ako je korisnik misem kliknuo na pocetak igre?
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if (pos[0] >= dims.WIDTH // 2 + dims.cell_size + dims.cell_size // 2 and pos[0] <= dims.WIDTH // 2 + dims.cell_size + dims.cell_size // 2 + 2 * dims.cell_size and pos[1] >= dims.HEIGHT // 2 + dims.cell_size and pos[1] <= dims.HEIGHT // 2 + 2 * dims.cell_size):
                    got_size = True

        # Za slucaj da je velicina i dalje 0?
        if got_size:
            if board_size <= 0:
                got_size = False

        pygame.display.update()

    # Ako smo kliknuli na dugme za zatvaranje prozora, zatvaramo prozor i tjt:
    if quit_event:
        return None

    # Inace, imamo sve, mozemo da pocnemo sa igrom:
    dim = Dims(board_size)          # Inicijalizujemo dimenzije
    print(first_player, board_size) # Stampa za proveru

    return (first_player, board_size, dim)

# Kreiranje matrice dimenzije dim x dim u memoriji:
def create_board(dim: int) -> list[list[str]]:
    table: list = list()
    for rw in range(0, dim):
        table.append(list())
        for cl in range(0, dim):
            table[rw].append(' ')
    return table

# Crtanje inicijalnog stanja tabele na prozoru:
def draw_board(win, dims: Dims):
    # Pozadina
    win.fill(BACKGROUND)

    # Iscrtavanje kvadratica tabele: 
    is_brown: bool = True
    for row in range(1, dims.rows + 1):
        if dims.rows % 2 == 0:
            is_brown = not is_brown
        for col in range(1, dims.cols + 1):
            color = BROWN if is_brown else WHITE
            is_brown = not is_brown
            pygame.draw.rect(win, color, (row * dims.cell_size, col * dims.cell_size, dims.cell_size, dims.cell_size))
    
    # Gornji i donji tekst na tabeli:
    for i in range(1, dims.cols + 1):
        
        # Inicijalizacija teksta koji se ispisuje:
        text = font.render(LETTER_ARRAY[i-1], True, OUTLINE, None)
        text_rect = text.get_rect()

        # Ispis u gornjem redu:
        text_rect.center = (i * dims.cell_size + dims.cell_size // 2, dims.cell_size // 2)
        WIN.blit(text, text_rect)

        # Ispis u donjem redu:
        text_rect.center = (i * dims.cell_size + dims.cell_size // 2, (dims.rows + 1) * dims.cell_size + dims.cell_size // 2)
        WIN.blit(text, text_rect)

    # Levi i desni tekst na tabeli:
    num: int = 0
    for i in range(dims.rows, 0, -1):

        # Inicijalizacija broja koji se ispisuje:
        text = font.render(str(num), True, OUTLINE, None)
        text_rect = text.get_rect()
        num = num + 1

        # Ispis u levoj koloni:
        text_rect.center = ( dims.cell_size // 2, i * dims.cell_size + dims.cell_size // 2)
        WIN.blit(text, text_rect)

        # Ispis u desnoj koloni:
        text_rect.center = ( (dims.cols + 1) * dims.cell_size + dims.cell_size // 2, i * dims.cell_size + dims.cell_size // 2)
        WIN.blit(text, text_rect)

# Racunanje pozicije polja u memoriji na osnovu dimenzija prozora i pozicije prozora na koju je 
# korisnik kliknuo:
def get_cell_pos(clicked_pos, dims: Dims) -> tuple:

    x_temp = clicked_pos[0]
    y_temp = clicked_pos[1]

    x_pos: int = int(x_temp / dims.cell_size)
    y_pos: int = int(y_temp / dims.cell_size)

    # Ukoliko smo kliknuli van okvira tabele, onda se vraca tuple(None, None) kao ne-validan potez:
    # (Ne validan u pogledu pozicije na koju je kliknuto, postoji funkcija koja ispituje i validnost poteza
    # u pogledu zauzetosti pozicije i dimenzije figure koja se postavlja);
    if (x_pos < 1 or y_pos < 1) or (x_pos > dims.rows or y_pos > dims.cols):
        return (None, None)

    return (dims.rows - y_pos, x_pos - 1)

# Postavljanje figure na tablu / u memoriji i iscrtavanje na klijentskom prozoru;
def set_figure(win, pos: tuple[int, int], player: bool, counter: int, table: list[list[str]], dims: Dims) -> bool: 
    
    # Da li je potez validan u pogledu zauzetosti polja:
    res = check_move(player, table, pos[0], pos[1])

    # Vracamo obavestenje da nismo postavili figuru na dato polje:
    if not res:
        return False

    # Inace mozemo da postavimo!
    # Postavljanje u slucaju da figuru postavlja igrac X:
    if player:

        # Iscrtavanje figure igraca X sa pocetkom u datoj poziciji:
        pygame.draw.rect(win, PIECE_X_COLOR, ((pos[1] + 1) * dims.cell_size + dims.piece_offset, (dims.rows - pos[0] - 1) * dims.cell_size + dims.piece_offset, dims.piece_short, dims.piece_long), 0, 5)

        # Ispis rednog broja poteza na vrh figure:
        text = font.render(str(counter), True, OUTLINE, None)
        text_rect = text.get_rect()
        text_rect.center = ((pos[1] + 1) * dims.cell_size + dims.piece_offset + dims.piece_short // 2, (dims.rows - pos[0] - 1) * dims.cell_size + dims.piece_offset + dims.piece_long // 2)

        win.blit(text, text_rect)

        # Postavljanje figure u memoriji:
        table[pos[0]][pos[1]] = 'X'
        table[pos[0] + 1][pos[1]] = 'X'

        # Vracamo odgovor da je figure uspesno postavljena:
        return True

    else:
        # Postavljanje u slucaju da figuru postavlja igrac X:
        
        # Iscrtavanje figure igraca Y sa pocetkom u datoj poziciji:
        pygame.draw.rect(win, PIECE_O_COLOR, ((pos[1] + 1) * dims.cell_size + dims.piece_offset, (dims.rows - pos[0]) * dims.cell_size + dims.piece_offset, dims.piece_long, dims.piece_short), 0, 5)

        # Ispis rednog broja poteza na vrh figure:
        text = font.render(str(counter), True, OUTLINE, None)
        text_rect = text.get_rect()
        text_rect.center = ((pos[1] + 1) * dims.cell_size + dims.piece_offset + dims.piece_long // 2, (dims.rows - pos[0]) * dims.cell_size + dims.piece_offset + dims.piece_short // 2)

        win.blit(text, text_rect)

        # Postavljanje figure u memoriji:
        table[pos[0]][pos[1]] = 'O'
        table[pos[0]][pos[1] + 1] = 'O'

        # Vracamo odgovor da je figure uspesno postavljena:
        return True


# Proverava da li je moguce postaviti figuru datog igraca na datu poziciju:
def check_move(player: bool, table: list[list[str]], x: int, y: int) -> bool:

    # Provera da li je indeks koji smo uneli uopste moguc za datu matricu:
    if (x < 0 or x >= len(table)) or (y < 0 or y >= len(table)):
        return False

    if player:  
        # Za slucaj da trenutno treba da igra X: 
        # Provera edge-case-ova da li je moguce postavljanje na datoj poziciji za igraca X:
        # Da je x barem 2 polja manji od max visine tabele? Kako bi stala figura koja je visine 2, duzine 1
        if x > len(table) - 2:
            return False

        # Provera da li su pozicije uopste slobodne za igraca O:
        if table[x][y] == ' ' and table[x+1][y] == ' ':
            return True
        else:
            return False

    else:   
        # Za slucaj da trenutno treba da igra O:

        # Provera edge-case-ova da li je moguce postavljanje na datoj poziciji za igraca O:
        # Da je y barem 2 polja manji od max duzine tabele? Kako bi stala figura koja je visine 1, duzine 2
        if y > len(table) - 2:
            return False

        # Provera da li su pozicije uopste slobodne za igraca X:
        if table[x][y] == ' ' and table[x][y+1] == ' ':
            return True
        else:
            return False

# Funkcija koja proverava da li je igracu koji je prosledjen (min/max) preostalo mogucih poteza, odnosno da li
# smo dosli do kraja igre:
def is_end(player: bool, table: list[list[str]]) -> bool:
    for i in range(0, len(table)):
        for j in range(0, len(table[i])):
            if (table[i][j]) == ' ' and (check_move(player, table, i, j)):
               return False
    return True


# Generisemo sva moguca stanja u koja moze da predje tabela na osnovu prosledjenog stanja
# i informacije ko sledeci igra;
# [player ==  True] -> X 
# [player == False] -> O
def possible_states(table: list[list[str]], dim: int, player: bool) -> list[tuple[list[list[str]], int, int]] or None:
    # Cuvamo sva moguca stanja u koja moze da predje trenutno stanje:
    states: list = list()

    # Pokusavamo da postavimo figuru na svaku mogucu poziciju:
    for x in range(0, dim):
        for y in range(0, dim):
            if table[x][y] == ' ' and check_move(player, table, x, y):
                
                # Kopiramo tabelu, kako bi mogli da nastavimo sa ispitivanjem: 
                new_table: list[list[str]] = copy.deepcopy(table)
                
                # Postavljamo odgovarajucu figuru na zadatu poziciju:
                if player:
                    new_table[x][y] = 'X'
                    new_table[x+1][y] = 'X'
                else:
                    new_table[x][y] = 'O'
                    new_table[x][y+1] = 'O'

                # Dodajemo stanje u listu mogucih:
                states.append((new_table, x, y))
    
    # Da ne bi vratio praznu listu, vec podatak tipa None ukoliko nema mogucih stanja:
    if states:
        return states
    else:
        return None

# Funkcija koja vrsi evaluaciju prosledjenog stanja tabele i igraca koji je sledeci na redu:
# Sto manja vrednost, to bolje!
def evaluate_state(state: list[list[str]], player: bool, dim: int) -> int:

    # Heuristika se racuna drugacije za min i max igraca: 
    state_count = dim * dim if not player else 0
    step = -1 if not player else 1

    for x in range(0, dim):
        for y in range(0, dim):
            if state[x][y] == ' ' and check_move(player, state, x, y):
                state_count += step
    
    return state_count


# Funkcija koju zovemo kada je u stablu pretrage red na max igraca:
def max_value(state: list[list[str]], depth: int, alpha, beta, player: bool, dim: int, x_pos: int, y_pos: int) -> tuple[list[list[str]], int, int, int]:

    # Da ne bi generisali bezveze ukoliko smo dosli do max dubine:
    if depth == 0:
        return (state, evaluate_state(state, player, dim), x_pos, y_pos)

    # Izvlacimo sva moguca stanja u koja mozemo da predjemo iz trenutnog:
    state_list = possible_states(state, dim, player)
    
    # Ukoliko nema vise mogucih poteza, 
    if state_list == None:
        return (state, evaluate_state(state, player, dim), x_pos, y_pos)

    # Obradjujemo listu mogucih stanja:
    for st in state_list:
        alpha = max(alpha, min_value(st[0], depth - 1, alpha, beta, not player, dim, st[1], st[2]), key = lambda x: x[1])
        if alpha[1] >= beta[1] and check_move(player, state, beta[2], beta[3]):
            return (beta[0], evaluate_state(beta[0], player, dim), beta[2] if x_pos == None else x_pos, beta[3] if y_pos == None else y_pos)

    return (alpha[0], evaluate_state(alpha[0], player, dim), alpha[2] if x_pos == None else x_pos, alpha[3] if y_pos == None else y_pos)


# Funkcija koju zovemo kada je u stablu pretrage red na min igraca:
def min_value(state: list[list[str]], depth: int, alpha, beta, player: bool, dim: int, x_pos: int, y_pos: int) -> tuple[list[list[str]], int, int, int]:

    # Da ne bi generisali bezveze ukoliko smo dosli do max dubine:
    if depth == 0:
        return (state, evaluate_state(state, player, dim), x_pos, y_pos)

    # Izvlacimo sva moguca stanja u koja mozemo da predjemo iz trenutnog:
    state_list = possible_states(state, dim, player)
    
    # Ukoliko nema vise mogucih poteza, 
    if state_list == None:
        return (state, evaluate_state(state, player, dim), x_pos, y_pos)

    # Obradjujemo listu mogucih stanja:
    for st in state_list:
        beta = min(beta, max_value(st[0], depth - 1, alpha, beta, not player, dim, st[1], st[2]), key = lambda x: x[1])
        if beta[1] <= alpha[1] and check_move(player, state, alpha[2], alpha[3]):
            return (alpha[0], evaluate_state(alpha[0], player, dim), alpha[2] if x_pos == None else x_pos, alpha[3] if y_pos == None else y_pos)
    
    return (beta[0], evaluate_state(beta[0], player, dim), beta[2] if x_pos == None else x_pos, beta[3] if y_pos == None else y_pos)


# Pokretanje min-max algoritma, mada posto je igrac X (racunar) uvek max, poziva se samo max_value:
def min_max(state: list[list[str]], player: bool, depth: int, dim: int) -> tuple[list[list[str]], int, int, int]:
    if player:
        return max_value(state, depth, (state, -1000, 0, 0), (state, 1000, 0, 0), player, dim, None, None)
    else:
        return min_value(state, depth, (state, -1000, 0, 0), (state, 1000, 0, 0), player, dim, None, None)

main(dims)