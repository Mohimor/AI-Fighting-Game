import json
import math
import sys
import time
from copy import deepcopy

class Agent:
    
    
    
    """
    این تابع برای وزن دهی به یکسری عوامل هست 
    که با توجه به اولویتشون اونارو نوشتم
    """
    def initial(self):
        self.weights = {
            'health_diff': 1.0,
            'distance_x': -1.8,
            'distance_y': -1.8,
            'light_attack': 1.4,
            'heavy_attack': 1.6,
            'opponent_cooldown': 1.8,
            'corner_penalty': -1.8,
            'good_range': 1.8,
            'opponent_attacking': -1.6,
            'too_close_penalty': -2.2,
            'height_advantage': 1.4,
            'same_height': 1.2
        }
        self.search_depth = 2
        self.transposition_table = {}
        self.start_time = None
        self.cutoff_depth = 0
        
        
        
        

    def _get_state_key(self, state, depth, max_player):
        key_parts = [
            f"hp{state['health_player']}",
            f"oh{state['health_opponent']}",
            f"px{state['x_player']//10}",
            f"py{state['y_player']//10}",
            f"ox{state['x_opponent']//10}",
            f"oy{state['y_opponent']//10}",
            f"cl{state['cooldown_player_light']}",
            f"ch{state['cooldown_player_heavy']}",
            f"cd{state['cooldown_player_dash']}",
            f"ol{state['cooldown_opponent_light']}",
            f"oh{state['cooldown_opponent_heavy']}",
            f"oa{int(state['opponent_attacking'])}",
            f"d{depth}",
            f"m{int(max_player)}"
        ]
        return "|".join(key_parts)
    
    
    
    
    """
    در اینجا پیاده سازی لاجیک فیزیکی اکشن هارو داریم
    که هر حرکت چه تغییری در موقعیت ایجنت 
    در صفحه بازی ایجاد میکنه
    """
    def action(self, state, action, is_player=True):
        new_state = deepcopy(state)
        if is_player:
            if action['move'] == 'left':
                new_state['x_player'] = max(60, state['x_player'] - 5)
            elif action['move'] == 'right':
                new_state['x_player'] = min(940, state['x_player'] + 5)
            if action['jump']:
                new_state['y_player'] = max(170, state['y_player'] - 30)
            if action['attack'] == 1:
                new_state['cooldown_player_light'] = 25
                distance = abs(new_state['x_player'] - new_state['x_opponent'])
                if distance < 180:
                    new_state['health_opponent'] = max(0, state['health_opponent'] - 10)
            elif action['attack'] == 2:
                new_state['cooldown_player_heavy'] = 100
                distance = abs(new_state['x_player'] - new_state['x_opponent'])
                if distance < 180:
                    new_state['health_opponent'] = max(0, state['health_opponent'] - 20)
            if action['dash'] == 'left':
                new_state['x_player'] = max(60, state['x_player'] - 30)
                new_state['cooldown_player_dash'] = 50
            elif action['dash'] == 'right':
                new_state['x_player'] = min(940, state['x_player'] + 30)
                new_state['cooldown_player_dash'] = 50
            if new_state['cooldown_player_light'] > 0:
                new_state['cooldown_player_light'] -= 1
            if new_state['cooldown_player_heavy'] > 0:
                new_state['cooldown_player_heavy'] -= 1
            if new_state['cooldown_player_dash'] > 0:
                new_state['cooldown_player_dash'] -= 1
        else:
            if new_state['x_opponent'] < new_state['x_player']:
                new_state['x_opponent'] = min(940, state['x_opponent'] + 5)
            else:
                new_state['x_opponent'] = max(60, state['x_opponent'] - 5)
            if new_state['cooldown_opponent_light'] > 0:
                new_state['cooldown_opponent_light'] -= 1
            if new_state['cooldown_opponent_heavy'] > 0:
                new_state['cooldown_opponent_heavy'] -= 1
        return new_state
    
    
    
    
    """
    چون یسری محدودیت در صورت پروژه داشتیم
    مثل تایم کول دان ها و ...،باید یک لاجیکی رو 
    پیاده میکردم که در هر فریم که داریم،
    میتونیم چه حرکاتی رو انجام بدیم
    """
    def possible_action(self, state):
        actions = []
        actions.append({'move': 'left', 'attack': None, 'jump': False, 'dash': None})
        actions.append({'move': 'right', 'attack': None, 'jump': False, 'dash': None})
        actions.append({'move': None, 'attack': None, 'jump': True, 'dash': None})
        if state['cooldown_player_light'] == 0:
            actions.append({'move': None, 'attack': 1, 'jump': False, 'dash': None})
        if state['cooldown_player_heavy'] == 0:
            actions.append({'move': None, 'attack': 2, 'jump': False, 'dash': None})
        if state['cooldown_player_dash'] == 0:
            actions.append({'move': None, 'attack': None, 'jump': False, 'dash': 'left'})
            actions.append({'move': None, 'attack': None, 'jump': False, 'dash': 'right'})
        actions.append({'move': 'left', 'attack': None, 'jump': True, 'dash': None})
        actions.append({'move': 'right', 'attack': None, 'jump': True, 'dash': None})
        return actions
    
    
    
    
    """
    این تابع برای تخمین مناسب بودن فاصلمون با ایجنت حریف هست
    که خود این هم یجورایی یک وزن دهی حساب میشه
    """

    def good_distance(self, distance_x, distance_y=None, is_player_jumping=False, is_opponent_jumping=False):
        if 120 <= distance_x < 180:
            score_x = 1.0
        elif 80 <= distance_x < 120:
            score_x = -0.6
        elif distance_x < 80:
            score_x = -0.5
        elif 180 <= distance_x < 250:
            score_x = 0.3
        elif 250 <= distance_x < 350:
            score_x = 0.0
        else:
            score_x = -0.8
        
        score_y = 0
        if distance_y is not None:
            if distance_y < 30:
                score_y = 1.0
            elif distance_y < 80:
                score_y = 0.5
            elif distance_y < 150:
                score_y = 0.0
            else:
                score_y = -0.7
        
        if is_opponent_jumping and not is_player_jumping and distance_y > 50:
            score_y += 0.8
        
        return (score_x + score_y) / 2
    
    
    
    
    """
    تابع محاسبه فاصله تا گوشه زمین بازی هست 
    که مینیمم فاصله تا هردو گوشه برای ما مهمه
    """
    def distance_to_corner(self, x_position, width=1000):
        distance_to_center = abs(x_position - width / 2)
        return min(distance_to_center / (width / 2), 1.0)
    
    
    
    
    """
    توی تابع هیوریستیک ابتدا یسری متغیر محلی داریم 
    که با استفاده از عوامل وزن داری که داشتیم 
    مقدار دهی میشن.و در ادامه لاجیک هیوریستیک 
    رو پیاده میکنیم و خروجی رو به صورت
    یک امتیاز ریترن میکنیم.
    """
    def heuristic(self, state, depth_remaining=None):
        health_diff = state['health_player'] - state['health_opponent']
        distance_x = abs(state['x_player'] - state['x_opponent'])
        distance_y = abs(state['y_player'] - state['y_opponent'])
        is_opponent_jumping = state['y_opponent'] < 350
        is_player_jumping = state['y_player'] < 350
        corner_penalty = self.distance_to_corner(state['x_player'])
        range_advantage = self.good_distance(distance_x, distance_y, is_player_jumping, is_opponent_jumping)
        light_ready = state['cooldown_player_light'] == 0
        heavy_ready = state['cooldown_player_heavy'] == 0
        opponent_in_cooldown = (state['cooldown_opponent_light'] > 0 and state['cooldown_opponent_heavy'] > 0)
        
        score = 0
        score += self.weights['health_diff'] * health_diff
        score += self.weights['distance_x'] * min(distance_x / 500, 2.0)
        score += self.weights['distance_y'] * min(distance_y / 200, 2.0)
        
        if distance_x < 100:
            score += self.weights['too_close_penalty'] * (1 - distance_x / 100)
        
        if state['y_player'] < state['y_opponent']:
            height_advantage = (state['y_opponent'] - state['y_player']) / 100
            score += self.weights['height_advantage'] * min(height_advantage, 1.0)
        
        if distance_y < 50 and distance_x < 180:
            same_height_score = 1.0 - (distance_y / 50)
            score += self.weights['same_height'] * same_height_score
        
        if light_ready:
            score += self.weights['light_attack']
        if heavy_ready:
            score += self.weights['heavy_attack']
        if opponent_in_cooldown:
            score += self.weights['opponent_cooldown']
        
        score += self.weights['corner_penalty'] * corner_penalty
        score += self.weights['good_range'] * range_advantage
        
        if state['opponent_attacking']:
            if distance_x < 180:
                score -= abs(self.weights['opponent_attacking']) * 2
            else:
                score += self.weights['opponent_attacking']
        return score
    
    
    
    
    
    """
    درخت مین و مکس رو داریم که محدوده جستجوش تا عمق دو هست.
    از آلفا بتا کات هم استفاده شده برای بهینگی
    زمان و سریعتر شدن تصمیم گیری.
    """
    def minimax(self, state, depth, alpha, beta, max_player):
        current = self.search_depth - depth
        time_spent = time.time() - self.start_time
        
        if time_spent > 0.35:
            self.cutoff_depth = current
            return self.heuristic(state, depth), None, current
            
        if depth == 0 or state['health_player'] <= 0 or state['health_opponent'] <= 0:
            return self.heuristic(state, depth), None, current
            
        state_key = self._get_state_key(state, depth, max_player)
        if state_key in self.transposition_table:
            return self.transposition_table[state_key]
            
        if max_player:
            max_eval = -float('inf')
            best_action = None
            best_depth = current
            
            for act in self.possible_action(state):
                new_state = self.action(state, act, is_player=True)
                opponent_actions = [
                    {'move': 'left', 'attack': None, 'jump': False, 'dash': None},
                    {'move': 'right', 'attack': None, 'jump': False, 'dash': None},
                    {'move': None, 'attack': 1, 'jump': False, 'dash': None}
                ]
                min_opponent_eval = float('inf')
                action_depth = current
                
                for opp_action in opponent_actions[:3]:
                    opp_state = self.action(new_state, opp_action, is_player=False)
                    eval, _, eval_depth = self.minimax(opp_state, depth-1, alpha, beta, False)
                    if eval < min_opponent_eval:
                        min_opponent_eval = eval
                        action_depth = eval_depth
                        
                if min_opponent_eval > max_eval:
                    max_eval = min_opponent_eval
                    best_action = act
                    best_depth = action_depth
                    
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
                    
            result = (max_eval, best_action, best_depth)
            self.transposition_table[state_key] = result
            return result
        else:
            min_eval = float('inf')
            best_depth = current
            opponent_actions = [
                {'move': 'left', 'attack': None, 'jump': False, 'dash': None},
                {'move': 'right', 'attack': None, 'jump': False, 'dash': None},
                {'move': None, 'attack': 1, 'jump': False, 'dash': None}
            ]
            for opp_action in opponent_actions:
                new_state = self.action(state, opp_action, is_player=False)
                eval, _, eval_depth = self.minimax(new_state, depth-1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_depth = eval_depth
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            return min_eval, None, best_depth
        
        
        
        
        
    """
    این تابع مثل پل ارتباطی هست که خروجی کل فریم رو به صورت جیسان میسازه 
    و خروجی میده.البته دوتام خروجی که بست اکشن و اسکور 
    رو من خروجی دیباگ گذاشتم برای 
    لاگ فریم به فریم ترمینال.
    """
    def make_move(self, fighter_info, opponent_info, saved_data):
        self.start_time = time.time()
        self.cutoff_depth = 0
        
        state = {
            'health_player': fighter_info['health'],
            'health_opponent': opponent_info['health'],
            'x_player': fighter_info['x'],
            'y_player': fighter_info['y'],
            'x_opponent': opponent_info['x'],
            'y_opponent': opponent_info['y'],
            'cooldown_player_light': fighter_info['attack_cooldown'][0],
            'cooldown_player_heavy': fighter_info['attack_cooldown'][1],
            'cooldown_player_dash': fighter_info['dash_cooldown'],
            'cooldown_opponent_light': 25 if opponent_info['attacking'] else 0,
            'cooldown_opponent_heavy': 100 if opponent_info['attacking'] else 0,
            'opponent_attacking': opponent_info['attacking']
        }
        
        best_score, best_action, reached_depth = self.minimax(
            state,
            self.search_depth,
            -float('inf'),
            float('inf'),
            True
        )
        
        if best_action is None:
            best_action = {'move': 'right', 'attack': None, 'jump': False, 'dash': None}
            best_score = 0
        
        action = {
            "move": best_action.get('move'),
            "attack": best_action.get('attack'),
            "jump": best_action.get('jump', False),
            "dash": best_action.get('dash'),
            "debug": {
                "best_action": {
                    "move": best_action.get('move'),
                    "attack": best_action.get('attack'),
                    "jump": best_action.get('jump', False),
                    "dash": best_action.get('dash')
                },
                "score": round(best_score, 2)
            },
            "saved_data": saved_data
        }
        
        self.transposition_table.clear()
        return action

def make_move(fighter_info, opponent_info, saved_data):
    agent = Agent()
    agent.initial()
    result = agent.make_move(fighter_info, opponent_info, saved_data)
    return result

if __name__ == "__main__":
    input_data = input()
    json_data = json.loads(input_data)
    fighter_info = json_data["fighter"]
    opponent_info = json_data["opponent"]
    saved_data = json_data.get("saved_data", {})
    result = make_move(fighter_info, opponent_info, saved_data)
    print(json.dumps(result))