import random
import os
import sys
import pygame
import time
import asyncio
    

pygame.init()

HEIGHT = 800
WIDTH = 800

screen = pygame.display.set_mode((HEIGHT, WIDTH))

font = pygame.font.Font(None, 36)
BLACK = (0,0,0)

starting_card_display_width = WIDTH/2

class Card:
    def __init__(self, image, value, suit, flipped=False):
        self.image = image
        self.value = value
        self.suit = suit
        self.flipped = flipped


async def start_new_round(cards: list[Card], player_cards: list[Card], dealer_cards: list[Card]):
    player_cards.clear()
    dealer_cards.clear()
    await hit(cards, player_cards, dealer_cards)
    await hit(cards, player_cards, dealer_cards)
    await hit_dealer(cards, player_cards, dealer_cards)
    await hit_dealer(cards, player_cards, dealer_cards)
    dealer_cards[1].flipped = True

def check_blackjacks(player_cards: list[Card], dealer_cards: list[Card]):
    player_blackjack = False
    dealer_blackjack = False
    if player_cards[0].value == 11 or player_cards[1].value == 11:
        if player_cards[0].value == 10 or player_cards[1].value == 10:
            player_blackjack = True
    if dealer_cards[0].value == 11 or dealer_cards[1].value == 11:
        if dealer_cards[0].value == 10 or dealer_cards[1].value == 10:
            dealer_blackjack = True
    return (player_blackjack, dealer_blackjack)

async def hit(cards, player_cards, dealer_cards):
    try:
        player_cards.append(cards.pop())
    except:
        await new_game(cards, screen)
        remove_duplicates(cards, player_cards, dealer_cards)
        player_cards.append(cards.pop())

async def hit_dealer(cards, player_cards, dealer_cards):
    try:
        dealer_cards.append(cards.pop())
    except:
        await new_game(cards, screen)
        remove_duplicates(cards, player_cards, dealer_cards)
        dealer_cards.append(cards.pop())

def flip_dealer_card(cards, player_cards, dealer_cards: list[Card]):
    dealer_cards[1].flipped = False

def calc_score(player_cards) -> str:
    total = sum([x.value for x in player_cards if not x.flipped])
    if total > 21:
        for card in player_cards:
            if card.value == 11:
                total -= 10
                if total <= 21:
                    return str(total)
        return 'Bust'
    return str(total)

def remove_duplicates(cards, player_cards, dealer_cards):
    for card in cards:
        if card in player_cards or card in dealer_cards:
            cards.remove(card)

async def draw(screen, clock, player_cards, dealer_cards, player_score, dealer_score, result_text, bet_amount, money):
    screen.fill((0, 155, 0))
    dealer_offset = starting_card_display_width - 25 - (len(dealer_cards))*50
    player_offset = starting_card_display_width - 25 - (len(player_cards))*50
    for card in dealer_cards:
        if card.flipped:
            screen.blit(back_card.image, (dealer_offset,25))
        else:
            screen.blit(card.image, (dealer_offset,25))
            dealer_offset += 125
    for card in player_cards:
        screen.blit(card.image, (player_offset,500))
        player_offset += 125
    dealer_score_text = font.render(dealer_score, True, BLACK)
    score_text = font.render(player_score, True, BLACK)
    result = font.render(result_text, True, BLACK)
    bet_text = font.render('Bet: ' + str(bet_amount), True, BLACK)
    money_text = font.render('Cash: ' + str(money), True, BLACK)
    screen.blit(dealer_score_text, (400,200))
    screen.blit(result, (400,300))
    screen.blit(score_text, (400,400))
    screen.blit(bet_text, (100, 400))
    screen.blit(money_text, (100, 450))
    pygame.display.flip()
    clock.tick(15)
    await asyncio.sleep(0)

async def new_game(cards, screen):
    screen.fill((0, 155, 0))
    screen.blit(font.render("Shuffling...", True, BLACK), (5, 5))
    pygame.display.flip()
    await asyncio.sleep(0)
    global back_card
    for _ in range(4):
        for file in os.listdir('./Assets'):
            img = pygame.image.load(os.path.join('./Assets', file))
            img = pygame.transform.scale(img, (100, 150))
            important_stuff = file.split('.')[0]
            value = important_stuff[0]
            if value == 'b':
                back_card = Card(img, 0, 'Back')
                continue
            suit = important_stuff[-1]
            if value == 'A':
                value = 11
            elif value == 'K' or value == 'Q' or value == 'J' or value == '1':
                value = 10
            else:
                value = int(value)
            
            if suit == 'c':
                suit = 'Clubs'
            elif suit == 's':
                suit = 'Spades'
            elif suit == 'd':
                suit = 'Diamonds'
            else:
                suit = 'Hearts'
            card = Card(img, value, suit)
            cards.append(card)
    random.shuffle(cards)


async def main():
    cards = []
    global back_card
    seed = int(time.time())
    random.seed(seed)
    clock = pygame.time.Clock()
    dealer_cards = []
    player_cards = []
    player_score =  ''
    dealer_score = ''
    result_text = ''
    await new_game(cards, screen)
    money = 300
    bet_amount = 0
    betting = True
    first_hit = True
    running = True
    while running:
        while betting:
            first_hit = True
            bet_change = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    betting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        player_score = ''
                        dealer_score = ''
                        betting = False
                        await start_new_round(cards, player_cards, dealer_cards)
                        blackjacks = check_blackjacks(player_cards, dealer_cards)
                        if blackjacks[0] and blackjacks[1]: # PUSH
                            flip_dealer_card(cards, player_cards, dealer_cards)
                            result_text = 'Push'
                            player_score = '21'
                            dealer_score = '21'
                            bet_amount = 0
                            betting = True
                            break
                        elif blackjacks[0]: # Player blackjack
                            flip_dealer_card(cards, player_cards, dealer_cards)
                            result_text = 'Blackjack you win!'
                            money += int(bet_amount*1.5)
                            bet_amount = 0
                            betting = True
                            player_score = '21'
                            dealer_score = calc_score(dealer_cards)
                            break
                        elif blackjacks[1]: # Dealer blackjack
                            flip_dealer_card(cards, player_cards, dealer_cards)
                            result_text = 'Dealer blackjack you lose'
                            money -= bet_amount
                            bet_amount = 0
                            betting = True
                            player_score = calc_score(player_cards)
                            dealer_score = '21'
                            break
                        result_text = ''
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN] and bet_amount >= 5:
                bet_amount -= 5  # Move left
            if keys[pygame.K_UP] and bet_amount <= money-5:
                bet_amount += 5  # Move right
            bet_amount += bet_change
            await draw(screen, clock, player_cards, dealer_cards, player_score, dealer_score, result_text, bet_amount, money)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and player_score != 'Bust' and dealer_score != 'Bust' and result_text == '' and first_hit and player_cards[0].value == player_cards[1].value: # split
                    first_hit = False
                if event.key == pygame.K_d and player_score != 'Bust' and dealer_score != 'Bust' and result_text == '' and first_hit and bet_amount*2 <= money: # double
                    first_hit = False
                    bet_amount *= 2
                    await hit(cards, player_cards, dealer_cards)
                    player_score = calc_score(player_cards)
                    if player_score == 'Bust':
                        flip_dealer_card(cards, player_cards, dealer_cards)
                        money -= bet_amount
                        bet_amount = 0
                        result_text = 'You Lose'
                        betting = True
                    else:
                        flip_dealer_card(cards, player_cards, dealer_cards)
                        dealer_score = calc_score(dealer_cards)
                        await draw(screen, clock, player_cards, dealer_cards, player_score, dealer_score, result_text, bet_amount, money)
                        time.sleep(.25)
                        while dealer_score != '17' and dealer_score != '18' and dealer_score != '19' and dealer_score != '20' and dealer_score != '21' and dealer_score != 'Bust':
                            await hit_dealer(cards, player_cards, dealer_cards)
                            dealer_score = calc_score(dealer_cards)
                            await draw(screen, clock, player_cards, dealer_cards, player_score, dealer_score, result_text, bet_amount, money)
                            time.sleep(.25)
                        if dealer_score == 'Bust':
                            money += bet_amount
                            bet_amount = 0
                            result_text = 'You Win!'
                            betting = True
                        elif int(dealer_score) == int(player_score):
                            result_text = 'Push'
                            bet_amount = 0
                            betting = True
                        elif int(dealer_score) > int(player_score):
                            money -= bet_amount
                            bet_amount = 0
                            result_text = 'You Lose'
                            betting = True
                        else:
                            money += bet_amount
                            bet_amount = 0
                            result_text = 'You Win!'
                            betting = True
                if event.key == pygame.K_SPACE and player_score != 'Bust' and dealer_score != 'Bust' and result_text == '':
                    first_hit = False
                    await hit(cards, player_cards, dealer_cards)
                    player_score = calc_score(player_cards)
                    if player_score == 'Bust':
                        flip_dealer_card(cards, player_cards, dealer_cards)
                        money -= bet_amount
                        bet_amount = 0
                        result_text = 'You Lose'
                        betting = True
                if event.key == pygame.K_RSHIFT and player_score != 'Bust' and dealer_score != 'Bust' and result_text == '':
                    flip_dealer_card(cards, player_cards, dealer_cards)
                    dealer_score = calc_score(dealer_cards)
                    await draw(screen, clock, player_cards, dealer_cards, player_score, dealer_score, result_text, bet_amount, money)
                    time.sleep(.25)
                    while dealer_score != '17' and dealer_score != '18' and dealer_score != '19' and dealer_score != '20' and dealer_score != '21' and dealer_score != 'Bust':
                        await hit_dealer(cards, player_cards, dealer_cards)
                        dealer_score = calc_score(dealer_cards)
                        await draw(screen, clock, player_cards, dealer_cards, player_score, dealer_score, result_text, bet_amount, money)
                        time.sleep(.25)
                    if dealer_score == 'Bust':
                        money += bet_amount
                        bet_amount = 0
                        result_text = 'You Win!'
                        betting = True
                    elif int(dealer_score) == int(player_score):
                        result_text = 'Push'
                        bet_amount = 0
                        betting = True
                    elif int(dealer_score) > int(player_score):
                        money -= bet_amount
                        bet_amount = 0
                        result_text = 'You Lose'
                        betting = True
                    else:
                        money += bet_amount
                        bet_amount = 0
                        result_text = 'You Win!'
                        betting = True
        dealer_score = calc_score(dealer_cards)
        player_score = calc_score(player_cards)
        await draw(screen, clock, player_cards, dealer_cards, player_score, dealer_score, result_text, bet_amount, money)
    pygame.quit()
    sys.exit()

asyncio.run(main())