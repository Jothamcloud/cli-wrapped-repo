#!/usr/bin/env python3
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import random

# ANSI colors
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'
CLEAR = '\033[2J\033[H'

def print_banner():
    print(CLEAR + f"""{YELLOW}
    $$$$$$\  $$\       $$$$$$\        $$\      $$\                                                         $$\ 
   $$  __$$\ $$ |      \_$$  _|       $$ | $\  $$ |                                                        $$ |
   $$ /  \__|$$ |        $$ |         $$ |$$$\ $$ | $$$$$$\  $$$$$$\   $$$$$$\   $$$$$$\    $$$$$$\   $$$$$$$ |
   $$ |      $$ |        $$ |         $$ $$ $$\$$ |$$  __$$\ \____$$\  $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$ |
   $$ |      $$ |        $$ |         $$$$  _$$$$ |$$ |  \__|$$$$$$$ | $$ /  $$ |$$ /  $$ |$$$$$$$$ |$$ /  $$ |
   $$ |  $$\ $$ |        $$ |         $$$  / \$$$ |$$ |     $$  __$$ | $$ |  $$ |$$ |  $$ |$$   ____|$$ |  $$ |
   \$$$$$$  |$$$$$$$$\ $$$$$$\        $$  /   \$$ |$$ |     \$$$$$$$ | $$$$$$$  |$$$$$$$  |\$$$$$$$\ \$$$$$$$ |
    \______/ \________|\______|       \__/     \__|\__|      \_______| $$  ____/ $$  ____/  \_______| \_______|
                                                                       $$ |      $$ |                            
                                                                       $$ |      $$ |
                                                                       \__|      \__|
    {RESET}""")

def get_shell_history_file():
    """Get the history file based on user's shell"""
    home = str(Path.home())
    shell = os.environ.get('SHELL', '').lower()
    
    history_files = {
        'bash': f"{home}/.bash_history",
        'zsh': f"{home}/.zsh_history",
        'fish': f"{home}/.local/share/fish/fish_history",
    }
    
    for shell_name, history_path in history_files.items():
        if os.path.exists(history_path):
            return history_path, shell_name
            
    return history_files['bash'], 'bash'

def read_history(file_path, shell_type):
    """Read command history based on shell type"""
    commands = []
    
    # First try reading directly from the history file
    if os.path.exists(file_path):
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                if shell_type == 'zsh':
                    for line in f:
                        if ': ' in line:
                            cmd = line.split(': ', 1)[1].strip()
                            if cmd and not cmd.startswith('cli-wrapped'):
                                commands.append(cmd)
                elif shell_type == 'fish':
                    for line in f:
                        if 'cmd:' in line:
                            cmd = line.split('cmd:', 1)[1].strip().strip('"')
                            if cmd and not cmd.startswith('cli-wrapped'):
                                commands.append(cmd)
                else:  # bash and others
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            cmd = line.strip()
                            if not cmd.startswith('cli-wrapped'):
                                commands.append(cmd)
        except Exception as e:
            pass

    # If no commands found from file, try getting current session commands
    if not commands:
        try:
            current = os.popen('fc -l -500 2>/dev/null || history').read().strip().split('\n')
            if current and current[0]:
                for cmd in current:
                    # Remove command numbers and whitespace
                    parts = cmd.split(None, 1)
                    if len(parts) > 1:
                        cmd = parts[1].strip()
                        if cmd and not cmd.startswith('cli-wrapped'):
                            commands.append(cmd)
        except:
            pass

    # Return all commands without deduplication
    return [cmd for cmd in commands if cmd]

def get_dev_personality(cmd_counter):
    personalities = {
        'Git Wizard 🧙‍♂️': {
            'commands': ['git', 'gh', 'gitlab', 'commit', 'push', 'pull'],
            'message': "Merging branches like a magic spell! Your git-fu is legendary!"
        },
        'Docker Captain 🐋': {
            'commands': ['docker', 'docker-compose', 'kubectl', 'container'],
            'message': "Sailing the container seas! Your pods are always shipshape!"
        },
        'Backend Architect 🏗️': {
            'commands': ['python', 'node', 'npm', 'postgresql', 'mongo'],
            'message': "Building digital castles in the cloud! Your APIs are works of art!"
        },
        'System Ninja 🥷': {
            'commands': ['systemctl', 'sudo', 'apt', 'service', 'dpkg', 'journalctl'],
            'message': "Silently maintaining the system! The terminal trembles at your power!"
        },
        'File Samurai ⚔️': {
            'commands': ['ls', 'cd', 'tree', 'find', 'cp', 'mv'],
            'message': "Slicing through directories with precision! Your filesystem fears you!"
        },
        'Shell Alchemist 🧪': {
            'commands': ['grep', 'sed', 'awk', 'curl', 'wget', 'ssh'],
            'message': "Transforming text into gold! Your one-liners are pure magic!"
        },
        'Terminal Explorer 🗺️': {
            'commands': ['ls', 'cd', 'clear', 'cat', 'echo', 'less'],
            'message': "Charting new paths in the command line universe! Adventure awaits!"
        }
    }
    
    scores = {}
    for personality, data in personalities.items():
        score = sum(cmd_counter.get(cmd, 0) for cmd in data['commands'])
        if score > 0:
            scores[personality] = score
            
    if not scores:
        return "Terminal Apprentice 🌱", "Beginning your journey in the command line arts!"
    
    top_personality = max(scores.items(), key=lambda x: x[1])
    return top_personality[0], personalities[top_personality[0]]['message']

def get_fun_fact(cmd_counter):
    facts = [
        # Git facts
        ("🌳 You've planted quite the git forest!", lambda c: c.get('git', 0) > 10),
        ("🔍 Always exploring new repos, aren't you?", lambda c: any(cmd.startswith('git clone') for cmd in c.keys())),
        ("📝 Writing git commit poetry!", lambda c: any(cmd.startswith('git commit') for cmd in c.keys())),
        ("🚀 To infinity and beyond with those pushes!", lambda c: any(cmd.startswith('git push') for cmd in c.keys())),
        ("🎣 Pulling in code like a pro fisher!", lambda c: any(cmd.startswith('git pull') for cmd in c.keys())),
        
        # System commands
        ("✨ Your terminal sparkles with those clear commands!", lambda c: c.get('clear', 0) > 5),
        ("🧭 Who needs 'ls' when you know your way around?", lambda c: c.get('cd', 0) > c.get('ls', 0)),
        ("👑 Sudo? More like sudo-god mode!", lambda c: c.get('sudo', 0) > 5),
        ("⚡ Lightning fast with those system commands!", lambda c: c.get('systemctl', 0) > 3),
        ("🔍 Directory detective extraordinaire!", lambda c: c.get('ls', 0) > 10),
        
        # Fun personality-based facts
        ("🎮 Commands are your video game!", lambda c: len(c) > 100),
        ("🎨 Your terminal is your canvas!", lambda c: c.get('vim', 0) > 5),
        ("🚄 Speed demon on the command line!", lambda c: c.get('alias', 0) > 3),
        ("🎵 Dancing with the directory structure!", lambda c: c.get('cd', 0) > 20),
        ("🌟 Making the terminal your happy place!", lambda c: c.get('cowsay', 0) > 0),
        
        # Random fun ones
        ("🎪 Your terminal is more exciting than a circus!", lambda c: True),
        ("🎭 Every command tells a story!", lambda c: True),
        ("🎪 You're the ringmaster of this terminal!", lambda c: True),
        ("🎨 Painting masterpieces with keystrokes!", lambda c: True)
    ]
    
    matching_facts = [fact for fact, condition in facts if condition(cmd_counter)]
    return random.choice(matching_facts) if matching_facts else "🌟 Writing your unique command line story!"

def analyze_history():
    print_banner()
    
    history_file, shell_type = get_shell_history_file()
    commands = read_history(history_file, shell_type)
    
    if not commands:
        print(f"\n{YELLOW}{BOLD}WELCOME TO THE COMMAND LINE ADVENTURE!{RESET}")
        print(f"\n{GREEN}Your journey begins here! Try these magical incantations:{RESET}")
        print(f"\n{BLUE}ls{RESET} - Reveal hidden treasures")
        print(f"{BLUE}cd{RESET} - Traverse the directory realms")
        print(f"{BLUE}pwd{RESET} - Discover your current location")
        print(f"{BLUE}mkdir{RESET} - Create new realms")
        print(f"{BLUE}touch{RESET} - Conjure new files")
        print(f"\n{GREEN}{BOLD}Pro tip:{RESET} The up arrow reveals past commands!")
        return

    cmd_counter = Counter(commands)
    total = len(commands)
    unique = len(set(commands))
    
    if total < 10:
        print(f"\n{YELLOW}{BOLD}LEVEL UP IN PROGRESS!{RESET}")
        print(f"{GREEN}You've cast {total} command spells so far!{RESET}")
        print(f"Just {10-total} more to unlock your full CLI Wrapped experience!")
        print(f"\n{BLUE}Keep exploring, future command line warrior!{RESET} 🚀")
        return

    top_cmds = cmd_counter.most_common(5)
    personality, message = get_dev_personality(cmd_counter)
    fun_fact = get_fun_fact(cmd_counter)

    print(f"\n{YELLOW}{BOLD}YOUR DEV PERSONALITY{RESET}")
    print(f"{BLUE}{BOLD}{personality}{RESET}")
    print(f"{message}")
    
    print(f"\n{YELLOW}{BOLD}FUN FACT{RESET}")
    print(f"{RED}{BOLD}{fun_fact}{RESET}")
    
    print(f"\n{YELLOW}{BOLD}COMMAND STATS{RESET}")
    print(f"{GREEN}Total Commands Cast: {BOLD}{total}{RESET}")
    print(f"{GREEN}Unique Spells Known: {BOLD}{unique}{RESET}")
    print(f"{GREEN}Preferred Scroll Type: {BOLD}{shell_type}{RESET}")
    
    print(f"\n{YELLOW}{BOLD}TOP COMMANDS{RESET}")
    for cmd, count in top_cmds:
        print(f"{cmd:<25} {count} times")

if __name__ == "__main__":
    analyze_history()
