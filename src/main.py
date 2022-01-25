import configparser

import pygame
from pygame.locals import *

import util.util as util

# Load configuration file and constants
config = configparser.ConfigParser()
config.read("config/config.ini")

TILESIZE = int(config["TILESIZE"]["TILESIZE"])
WHITE = pygame.Color(config["COLORS"]["WHITE"])
BLACK = pygame.Color(config["COLORS"]["BLACK"])
WHITE_HOVER = pygame.Color(config["COLORS"]["BLACK"] + "7a")
BLACK_HOVER = pygame.Color(config["COLORS"]["WHITE"] + "7a")
SELECTED = pygame.Color(config["COLORS"]["SELECTED"])


class Board:
    """Board representation"""

    def __init__(self, fen, screen):
        self.board = []
        self.background = self.draw_background(screen)
        self.pieces = pygame.sprite.Group()
        self.fen = fen
        self.parse_fen(self.fen)

    def parse_fen(self, fen):
        """Parse fen string"""
        fen = fen.split(" ")
        self.board = []

        for i, rank in enumerate(fen[0].split("/")):
            self.board.append([])
            # Replaces empty squares with empty strings
            for j, file in enumerate("".join([x if not x.isdigit() else " " * int(x) for x in rank])):
                if file.isalpha():
                    self.board[i].append(Piece(self.pieces, file, (i, j)))
                else:
                    self.board[i].append(None)

        self.turn = fen[1]
        self.castling = fen[2]
        self.en_passant = fen[3]
        self.half_move = int(fen[4])
        self.full_move = int(fen[5])

    def draw_background(self, screen):
        """Fill background"""
        background = pygame.Surface(screen.get_size()).convert()
        for i in range(8):
            for j in range(8):
                background.fill(WHITE if (((i + j) % 2) == 0) else BLACK,
                                (i * TILESIZE, j * TILESIZE, TILESIZE, TILESIZE))

        return background

    def draw_rect_alpha(self, surface, color, rect):
        """Draw rectangle with alpha"""
        shape_surface = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surface, color,
                         shape_surface.get_rect(), TILESIZE // 25)
        surface.blit(shape_surface, rect)

    def get_possible_moves(self, piece):
        """Return possible moves for piece"""

        # Special moves like en passant, castling, pawn promotion, etc.

        moves = []
        position = util.get_position_from_coordinates(piece.rect.center)
        if piece.name == "p":
            if piece.color == "w":
                if position[0] == 6 and self.board[position[0] - 2][position[1]] is None:
                    moves.append((position[0] - 2, position[1]))
                if self.board[position[0] - 1][position[1]] is None:
                    moves.append((position[0] - 1, position[1]))
                if position[1] > 0 and self.board[position[0] - 1][position[1] - 1] is not None and \
                        self.board[position[0] - 1][position[1] - 1].color != piece.color:
                    moves.append((position[0] - 1, position[1] - 1))
                if position[1] < 6 and self.board[position[0] - 1][position[1] + 1] is not None and \
                        self.board[position[0] - 1][position[1] + 1].color != piece.color:
                    moves.append((position[0] - 1, position[1] + 1))
            else:
                if position[0] == 1 and self.board[position[0] + 2][position[1]] is None:
                    moves.append((position[0] + 2, position[1]))
                if self.board[position[0] + 1][position[1]] is None:
                    moves.append((position[0] + 1, position[1]))
                if position[1] < 6 and self.board[position[0] + 1][position[1] - 1] is not None and \
                        self.board[position[0] + 1][position[1] - 1].color != piece.color:
                    moves.append((position[0] + 1, position[1] - 1))
                if position[1] < 0 and self.board[position[0] + 1][position[1] + 1] is not None and \
                        self.board[position[0] + 1][position[1] + 1].color != piece.color:
                    moves.append((position[0] + 1, position[1] + 1))

        if piece.name == "k":
            moves.append((position[0] - 1, position[1] - 1))
            moves.append((position[0] - 1, position[1] + 1))
            moves.append((position[0] + 1, position[1] - 1))
            moves.append((position[0] + 1, position[1] + 1))
            moves.append((position[0] - 1, position[1]))
            moves.append((position[0] + 1, position[1]))
            moves.append((position[0], position[1] - 1))
            moves.append((position[0], position[1] + 1))
        if piece.name == "n":
            moves.append((position[0] - 2, position[1] - 1))
            moves.append((position[0] - 2, position[1] + 1))
            moves.append((position[0] + 2, position[1] - 1))
            moves.append((position[0] + 2, position[1] + 1))
            moves.append((position[0] - 1, position[1] - 2))
            moves.append((position[0] - 1, position[1] + 2))
            moves.append((position[0] + 1, position[1] - 2))
            moves.append((position[0] + 1, position[1] + 2))
        if piece.name == "b" or piece.name == "q":
            for i in range(1, 8):
                if position[0] - i >= 0 and position[1] - i >= 0:
                    if self.board[position[0] - i][position[1] - i] is None:
                        moves.append((position[0] - i, position[1] - i))
                    else:
                        if self.board[position[0] - i][position[1] - i].color != piece.color:
                            moves.append((position[0] - i, position[1] - i))
                        break
            for i in range(1, 8):
                if position[0] - i >= 0 and position[1] + i < 8:
                    if self.board[position[0] - i][position[1] + i] is None:
                        moves.append((position[0] - i, position[1] + i))
                    else:
                        if self.board[position[0] - i][position[1] + i].color != piece.color:
                            moves.append((position[0] - i, position[1] + i))
                        break
            for i in range(1, 8):
                if position[0] + i < 8 and position[1] - i >= 0:
                    if self.board[position[0] + i][position[1] - i] is None:
                        moves.append((position[0] + i, position[1] - i))
                    else:
                        if self.board[position[0] + i][position[1] - i].color != piece.color:
                            moves.append((position[0] + i, position[1] - i))
                        break
            for i in range(1, 8):
                if position[0] + i < 8 and position[1] + i < 8:
                    if self.board[position[0] + i][position[1] + i] is None:
                        moves.append((position[0] + i, position[1] + i))
                    else:
                        if self.board[position[0] + i][position[1] + i].color != piece.color:
                            moves.append((position[0] + i, position[1] + i))
                        break
        if piece.name == "r" or piece.name == "q":
            for i in range(1, 8):
                if position[0] - i >= 0:
                    if self.board[position[0] - i][position[1]] is None:
                        moves.append((position[0] - i, position[1]))
                    else:
                        if self.board[position[0] - i][position[1]].color != piece.color:
                            moves.append((position[0] - i, position[1]))
                        break
            for i in range(1, 8):
                if position[0] + i < 8:
                    if self.board[position[0] + i][position[1]] is None:
                        moves.append((position[0] + i, position[1]))
                    else:
                        if self.board[position[0] + i][position[1]].color != piece.color:
                            moves.append((position[0] + i, position[1]))
                        break
            for i in range(1, 8):
                if position[1] - i >= 0:
                    if self.board[position[0]][position[1] - i] is None:
                        moves.append((position[0], position[1] - i))
                    else:
                        if self.board[position[0]][position[1] - i].color != piece.color:
                            moves.append((position[0], position[1] - i))
                        break
            for i in range(1, 8):
                if position[1] + i < 7:
                    if self.board[position[0]][position[1] + i] is None:
                        moves.append((position[0], position[1] + i))
                    else:
                        if self.board[position[0]][position[1] + i].color != piece.color:
                            moves.append((position[0], position[1] + i))
                        break

        return moves


class Piece(pygame.sprite.Sprite):
    """Piece representation"""

    def __init__(self, group, name, position):
        super().__init__()

        self.color = "w" if name.isupper() else "b"
        self.name = name.lower()

        self.image = pygame.transform.scale(pygame.image.load(
            f"res/{self.color}_{self.name}.png").convert_alpha(), (TILESIZE - TILESIZE // 4, TILESIZE - TILESIZE // 4))

        self.rect = self.image.get_rect()

       # Positions are row-major
        self.set_coordinates_from_position(position)

        self.add(group)

    def set_coordinates_from_position(self, position):
        """Set the x and y coordinates based on the grid position"""
        self.rect.x, self.rect.y = (
            position[1] * TILESIZE + TILESIZE // 8, position[0] * TILESIZE + TILESIZE // 8)


def main():

    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((TILESIZE * 8, TILESIZE * 8))
    pygame.display.set_caption("Chess")

    # Prepare game objects
    with open("res/start.fen", "r") as f:
        fen = f.read()

    board = Board(fen, screen)
    selected_piece = None
    clock = pygame.time.Clock()

    # Event loop
    while True:
        clock.tick(60)
        hovering_position = util.get_position_from_coordinates(
            pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    selected_piece = board.board[hovering_position[0]
                                                 ][hovering_position[1]]
                    if selected_piece:
                        selected_piece.rect.center = event.pos
                        offset_x = selected_piece.rect.x - event.pos[0]
                        offset_y = selected_piece.rect.y - event.pos[1]
                        original_position = hovering_position
                        possible_moves = board.get_possible_moves(
                            selected_piece)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and selected_piece:
                    captured_piece = board.board[hovering_position[0]
                                                 ][hovering_position[1]]

                    if (captured_piece and (captured_piece.color == selected_piece.color)) or (board.turn != selected_piece.color) or (hovering_position not in possible_moves):
                        selected_piece.set_coordinates_from_position(
                            original_position)
                        selected_piece = None
                    else:
                        if captured_piece and (captured_piece.color != selected_piece.color):
                            board.pieces.remove(captured_piece)
                            if captured_piece.name == "k":
                                # TODO: Game over and restart
                                pass
                        board.board[original_position[0]
                                    ][original_position[1]] = None
                        board.board[hovering_position[0]
                                    ][hovering_position[1]] = selected_piece

                        selected_piece.set_coordinates_from_position(
                            hovering_position)

                        selected_piece = None

                        board.turn = "w" if board.turn == "b" else "b"
                        board.half_move += 1

            elif event.type == MOUSEMOTION:
                if selected_piece:
                    selected_piece.rect.x = event.pos[0] + offset_x
                    selected_piece.rect.y = event.pos[1] + offset_y

        screen.blit(board.background, (0, 0))

        if (not selected_piece or selected_piece.color != board.turn or hovering_position not in [*possible_moves, original_position]):
            if ((hovering_position[0] + hovering_position[1]) % 2 == 0):
                color = WHITE_HOVER
            else:
                color = BLACK_HOVER
        else:
            color = SELECTED

        board.draw_rect_alpha(screen, color,
                              (hovering_position[1] * TILESIZE, hovering_position[0] * TILESIZE, TILESIZE, TILESIZE))

        board.pieces.update()
        board.pieces.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
